from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from telegram.error import Forbidden, RetryAfter, TelegramError

from app.database import session_scope
from app.models import ReminderDelivery, User

LOGGER = logging.getLogger(__name__)


@dataclass
class DueReminder:
    user_id: int
    telegram_user_id: int
    reminder_type: str
    intended_local_date: datetime.date
    intended_local_time: datetime.time
    intended_utc_at: datetime
    idempotency_key: str


class ReminderService:
    """Database-driven reminder delivery with idempotency and safe catch-up."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        grace_minutes: int = 10,
        catchup_minutes: int = 30,
    ) -> None:
        self.session_factory = session_factory
        self.grace_minutes = grace_minutes
        self.catchup_minutes = catchup_minutes

    def _is_quiet_hours(self, user: User, local_now: datetime) -> bool:
        if not user.quiet_hours_start or not user.quiet_hours_end:
            return False
        now_time = local_now.timetz().replace(tzinfo=None)
        start = user.quiet_hours_start
        end = user.quiet_hours_end
        if start <= end:
            return start <= now_time <= end
        return now_time >= start or now_time <= end

    def due_reminders(self, session: Session, now_utc: datetime) -> list[DueReminder]:
        now_utc = now_utc.astimezone(UTC)
        users = list(session.scalars(select(User).where(User.paused_reminders.is_(False))))
        due: list[DueReminder] = []

        for user in users:
            tz = ZoneInfo(user.timezone)
            local_now = now_utc.astimezone(tz)
            if self._is_quiet_hours(user, local_now):
                continue
            windows = [
                ("morning", user.morning_time, user.morning_enabled),
                ("afternoon", user.afternoon_time, user.afternoon_enabled),
                ("evening", user.evening_time, user.evening_enabled),
            ]
            for reminder_type, local_time, enabled in windows:
                if not enabled:
                    continue
                target_local = datetime.combine(local_now.date(), local_time, tzinfo=tz)
                target_utc = target_local.astimezone(UTC)
                minutes_since = (now_utc - target_utc).total_seconds() / 60
                if minutes_since < 0:
                    continue
                if minutes_since > self.catchup_minutes:
                    continue
                if minutes_since > self.grace_minutes:
                    continue

                idempotency_key = f"{user.id}:{reminder_type}:{local_now.date().isoformat()}:{local_time.isoformat()}"
                exists = session.scalar(select(ReminderDelivery).where(ReminderDelivery.idempotency_key == idempotency_key))
                if exists:
                    continue
                due.append(
                    DueReminder(
                        user_id=user.id,
                        telegram_user_id=user.telegram_user_id,
                        reminder_type=reminder_type,
                        intended_local_date=local_now.date(),
                        intended_local_time=local_time,
                        intended_utc_at=target_utc,
                        idempotency_key=idempotency_key,
                    )
                )
        return due

    async def process_due(self, bot, now_utc: datetime | None = None) -> int:
        now_utc = now_utc or datetime.now(tz=UTC)
        sent = 0
        with session_scope(self.session_factory) as session:
            due = self.due_reminders(session, now_utc)
            for item in due:
                delivery = ReminderDelivery(
                    user_id=item.user_id,
                    reminder_type=item.reminder_type,
                    intended_local_date=item.intended_local_date,
                    intended_local_time=item.intended_local_time,
                    intended_utc_at=item.intended_utc_at,
                    idempotency_key=item.idempotency_key,
                    status="pending",
                    attempts=0,
                )
                session.add(delivery)
                session.flush()

                text = f"{item.reminder_type.title()} reminder: keep your DisciplineOS mission moving with /today."
                try:
                    delivery.attempts += 1
                    await bot.send_message(chat_id=item.telegram_user_id, text=text)
                    delivery.status = "sent"
                    delivery.sent_at = datetime.now(tz=UTC)
                    sent += 1
                except RetryAfter as exc:
                    delivery.status = "failed"
                    delivery.last_error = f"rate_limited:{exc.retry_after}"
                except Forbidden:
                    delivery.status = "skipped"
                    delivery.last_error = "blocked_by_user"
                except TelegramError as exc:
                    delivery.status = "failed"
                    delivery.last_error = str(exc)
                    LOGGER.warning("Failed reminder delivery user=%s type=%s", item.user_id, item.reminder_type)
        return sent
