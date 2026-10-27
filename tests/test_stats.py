from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.database import session_scope
from app.services.habit_service import HabitService
from app.services.stats_service import StatsService


def _complete_all_single_habits(service: HabitService, user, when: datetime) -> None:
    for key in ["study", "exercise", "german", "reading", "content"]:
        service.mark_completion(user, key, when)
    service.mark_completion(user, "water", when, quantity=Decimal("2000"))
    for idx in range(5):
        service.mark_completion(user, "prayer", when + timedelta(minutes=idx), completion_key=f"{when.date()}-{idx}")


def test_daily_and_weekly_stats(session_factory):
    now = datetime(2026, 1, 14, 8, tzinfo=UTC)
    with session_scope(session_factory) as session:
        habits = HabitService(session)
        user = habits.register_or_get_user(1, None, None)
        _complete_all_single_habits(habits, user, now)

        stats = StatsService(session).summary(user, now)

    assert stats.today_percent == 100
    assert stats.weekly_percent >= 14


def test_current_and_best_streak(session_factory):
    now = datetime(2026, 1, 14, 8, tzinfo=UTC)
    with session_scope(session_factory) as session:
        habits = HabitService(session)
        user = habits.register_or_get_user(1, None, None)

        _complete_all_single_habits(habits, user, now - timedelta(days=2))
        _complete_all_single_habits(habits, user, now - timedelta(days=1))
        _complete_all_single_habits(habits, user, now)

        stats = StatsService(session).summary(user, now)

    assert stats.current_streak == 3
    assert stats.best_streak == 3
