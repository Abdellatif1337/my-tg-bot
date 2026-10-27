from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from app.database import session_scope
from app.services.habit_service import HabitService


def test_first_registration_creates_default_habits(session_factory, now_utc):
    with session_scope(session_factory) as session:
        service = HabitService(session)
        user = service.register_or_get_user(1, "owner", "Owner")
        habits = service.get_habits(user.id)
    assert len(habits) == 7


def test_duplicate_completion_blocked_for_single_daily_habit(session_factory, now_utc):
    with session_scope(session_factory) as session:
        service = HabitService(session)
        user = service.register_or_get_user(1, None, None)
        assert service.mark_completion(user, "study", now_utc) is True
        assert service.mark_completion(user, "study", now_utc) is False


def test_water_tracking_allows_multiple_entries(session_factory, now_utc):
    with session_scope(session_factory) as session:
        service = HabitService(session)
        user = service.register_or_get_user(1, None, None)
        assert service.mark_completion(user, "water", now_utc, quantity=Decimal("250"))
        assert service.mark_completion(user, "water", now_utc, quantity=Decimal("500"))
        consumed, remaining = service.water_status(user, now_utc)
    assert consumed == Decimal("750")
    assert remaining == Decimal("1250.00")


def test_prayer_tracking_allows_multiple_entries(session_factory, now_utc):
    with session_scope(session_factory) as session:
        service = HabitService(session)
        user = service.register_or_get_user(1, None, None)
        for idx in range(3):
            assert service.mark_completion(user, "prayer", now_utc + timedelta(minutes=idx), completion_key=f"p-{idx}")
        progress = service.today_progress(user, now_utc)
    assert progress.total_habits == 7
    assert progress.completed_habits == 0


def test_habit_can_be_disabled(session_factory, now_utc):
    with session_scope(session_factory) as session:
        service = HabitService(session)
        user = service.register_or_get_user(1, None, None)
        habit = service.toggle_habit(user.id, "reading")
        assert habit is not None
        assert habit.enabled is False
