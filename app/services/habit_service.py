from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Habit, HabitCompletion, User


DEFAULT_HABITS = [
    {
        "key": "study",
        "name": "Study",
        "description": "Complete a focused study session.",
        "daily_target": Decimal("1"),
        "target_unit": "session",
        "config_json": {"allow_multiple_per_day": False},
    },
    {
        "key": "exercise",
        "name": "Exercise",
        "description": "Complete a workout or planned physical activity.",
        "daily_target": Decimal("1"),
        "target_unit": "session",
        "config_json": {"allow_multiple_per_day": False},
    },
    {
        "key": "prayer",
        "name": "Prayer",
        "description": "Track daily prayer progress.",
        "daily_target": Decimal("5"),
        "target_unit": "prayers",
        "config_json": {"allow_multiple_per_day": True, "optional_for_streak": True},
    },
    {
        "key": "german",
        "name": "German",
        "description": "Practice German for at least 15 minutes.",
        "daily_target": Decimal("1"),
        "target_unit": "session",
        "config_json": {"allow_multiple_per_day": False},
    },
    {
        "key": "reading",
        "name": "Reading",
        "description": "Read for at least 10 minutes.",
        "daily_target": Decimal("1"),
        "target_unit": "session",
        "config_json": {"allow_multiple_per_day": False},
    },
    {
        "key": "water",
        "name": "Water",
        "description": "Record water intake.",
        "daily_target": Decimal("2000"),
        "target_unit": "ml",
        "config_json": {"allow_multiple_per_day": True, "increments": [100, 250, 500]},
    },
    {
        "key": "content",
        "name": "Content",
        "description": "Prepare or publish one piece of content.",
        "daily_target": Decimal("1"),
        "target_unit": "piece",
        "config_json": {"allow_multiple_per_day": False},
    },
]


@dataclass
class TodayProgress:
    completed_habits: int
    total_habits: int
    percent: int


class HabitService:
    def __init__(self, session: Session):
        self.session = session

    def register_or_get_user(self, telegram_user_id: int, username: str | None, display_name: str | None, timezone: str = "UTC") -> User:
        user = self.session.scalar(select(User).where(User.telegram_user_id == telegram_user_id))
        if user:
            return user
        user = User(telegram_user_id=telegram_user_id, username=username, display_name=display_name, timezone=timezone)
        self.session.add(user)
        self.session.flush()
        for habit_data in DEFAULT_HABITS:
            self.session.add(Habit(user_id=user.id, **habit_data))
        self.session.flush()
        return user

    def get_user_by_telegram_id(self, telegram_user_id: int) -> User | None:
        return self.session.scalar(select(User).where(User.telegram_user_id == telegram_user_id))

    def get_habits(self, user_id: int, enabled_only: bool = False) -> list[Habit]:
        query = select(Habit).where(Habit.user_id == user_id)
        if enabled_only:
            query = query.where(Habit.enabled.is_(True))
        query = query.order_by(Habit.id)
        return list(self.session.scalars(query))

    def mark_completion(
        self,
        user: User,
        habit_key: str,
        now_utc: datetime,
        quantity: Decimal = Decimal("1"),
        note: str | None = None,
        completion_key: str | None = None,
    ) -> bool:
        habit = self.session.scalar(select(Habit).where(Habit.user_id == user.id, Habit.key == habit_key, Habit.enabled.is_(True)))
        if not habit:
            return False
        local_date = now_utc.astimezone(ZoneInfo(user.timezone)).date()
        allow_multi = bool(habit.config_json.get("allow_multiple_per_day", False))
        if completion_key is None:
            completion_key = str(uuid4()) if allow_multi else "daily"

        completion = HabitCompletion(
            user_id=user.id,
            habit_id=habit.id,
            local_date=local_date,
            completed_at=now_utc,
            quantity=quantity,
            completion_key=completion_key,
            note=note,
        )
        self.session.add(completion)
        try:
            self.session.flush()
            return True
        except IntegrityError:
            self.session.rollback()
            return False

    def undo_daily_completion(self, user: User, habit_key: str, now_utc: datetime) -> bool:
        habit = self.session.scalar(select(Habit).where(Habit.user_id == user.id, Habit.key == habit_key))
        if not habit:
            return False
        local_date = now_utc.astimezone(ZoneInfo(user.timezone)).date()
        completion = self.session.scalar(
            select(HabitCompletion).where(
                HabitCompletion.user_id == user.id,
                HabitCompletion.habit_id == habit.id,
                HabitCompletion.local_date == local_date,
                HabitCompletion.completion_key == "daily",
            )
        )
        if not completion:
            return False
        self.session.delete(completion)
        self.session.flush()
        return True

    def water_status(self, user: User, now_utc: datetime) -> tuple[Decimal, Decimal]:
        habit = self.session.scalar(select(Habit).where(Habit.user_id == user.id, Habit.key == "water"))
        if not habit:
            return Decimal("0"), Decimal("0")
        local_date = now_utc.astimezone(ZoneInfo(user.timezone)).date()
        consumed = (
            self.session.scalar(
                select(func.coalesce(func.sum(HabitCompletion.quantity), 0)).where(
                    HabitCompletion.user_id == user.id,
                    HabitCompletion.habit_id == habit.id,
                    HabitCompletion.local_date == local_date,
                )
            )
            or Decimal("0")
        )
        remaining = max(Decimal(habit.daily_target) - Decimal(consumed), Decimal("0"))
        return Decimal(consumed), remaining

    def toggle_habit(self, user_id: int, habit_key: str) -> Habit | None:
        habit = self.session.scalar(select(Habit).where(Habit.user_id == user_id, Habit.key == habit_key))
        if not habit:
            return None
        habit.enabled = not habit.enabled
        self.session.flush()
        return habit

    def today_progress(self, user: User, now_utc: datetime) -> TodayProgress:
        habits = self.get_habits(user.id, enabled_only=True)
        if not habits:
            return TodayProgress(0, 0, 0)
        local_date = now_utc.astimezone(ZoneInfo(user.timezone)).date()

        completed = 0
        for habit in habits:
            amount = (
                self.session.scalar(
                    select(func.coalesce(func.sum(HabitCompletion.quantity), 0)).where(
                        HabitCompletion.user_id == user.id,
                        HabitCompletion.habit_id == habit.id,
                        HabitCompletion.local_date == local_date,
                    )
                )
                or Decimal("0")
            )
            if Decimal(amount) >= Decimal(habit.daily_target):
                completed += 1

        percent = int((completed / len(habits)) * 100)
        return TodayProgress(completed, len(habits), percent)
