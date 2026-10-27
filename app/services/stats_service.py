from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Habit, HabitCompletion, User


@dataclass
class StatsSummary:
    today_completed: int
    today_total: int
    today_percent: int
    weekly_percent: int
    current_streak: int
    best_streak: int


class StatsService:
    def __init__(self, session: Session):
        self.session = session

    def _daily_ratio(self, user: User, day: date) -> tuple[int, int]:
        habits = list(self.session.scalars(select(Habit).where(Habit.user_id == user.id, Habit.enabled.is_(True))))
        if not habits:
            return 0, 0

        completed = 0
        for habit in habits:
            amount = (
                self.session.scalar(
                    select(func.coalesce(func.sum(HabitCompletion.quantity), 0)).where(
                        HabitCompletion.user_id == user.id,
                        HabitCompletion.habit_id == habit.id,
                        HabitCompletion.local_date == day,
                    )
                )
                or Decimal("0")
            )
            if Decimal(amount) >= Decimal(habit.daily_target):
                completed += 1
        return completed, len(habits)

    def _day_is_complete(self, user: User, day: date) -> bool:
        completed, total = self._daily_ratio(user, day)
        return total > 0 and completed == total

    def _streaks(self, user: User, today: date) -> tuple[int, int]:
        first_completion_date = self.session.scalar(
            select(func.min(HabitCompletion.local_date)).where(HabitCompletion.user_id == user.id)
        )
        if not first_completion_date:
            return 0, 0

        current = 0
        cursor = today
        while self._day_is_complete(user, cursor):
            current += 1
            cursor -= timedelta(days=1)

        best = 0
        running = 0
        day = first_completion_date
        while day <= today:
            if self._day_is_complete(user, day):
                running += 1
                best = max(best, running)
            else:
                running = 0
            day += timedelta(days=1)
        return current, best

    def summary(self, user: User, now_utc: datetime) -> StatsSummary:
        local_now = now_utc.astimezone(ZoneInfo(user.timezone))
        today = local_now.date()
        today_completed, today_total = self._daily_ratio(user, today)
        today_percent = int((today_completed / today_total) * 100) if today_total else 0

        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        week_total_completed = 0
        week_total_slots = 0
        day = week_start
        while day <= week_end:
            completed, total = self._daily_ratio(user, day)
            week_total_completed += completed
            week_total_slots += total
            day += timedelta(days=1)
        weekly_percent = int((week_total_completed / week_total_slots) * 100) if week_total_slots else 0

        current, best = self._streaks(user, today)
        return StatsSummary(
            today_completed=today_completed,
            today_total=today_total,
            today_percent=today_percent,
            weekly_percent=weekly_percent,
            current_streak=current,
            best_streak=best,
        )
