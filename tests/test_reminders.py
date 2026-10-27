from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.database import session_scope
from app.services.habit_service import HabitService
from app.services.reminder_service import ReminderService


class FakeBot:
    def __init__(self):
        self.messages = []

    async def send_message(self, chat_id: int, text: str):
        self.messages.append((chat_id, text))


@pytest.mark.asyncio
async def test_due_reminders_respect_disable_and_pause(session_factory):
    with session_scope(session_factory) as session:
        service = HabitService(session)
        user = service.register_or_get_user(1, None, None)
        user.paused_reminders = True

    reminder = ReminderService(session_factory)
    bot = FakeBot()
    sent = await reminder.process_due(bot, datetime(2026, 1, 10, 8, 0, tzinfo=UTC))
    assert sent == 0


@pytest.mark.asyncio
async def test_duplicate_delivery_prevented(session_factory):
    with session_scope(session_factory) as session:
        service = HabitService(session)
        service.register_or_get_user(1, None, None)

    reminder = ReminderService(session_factory)
    bot = FakeBot()
    now = datetime(2026, 1, 10, 8, 1, tzinfo=UTC)
    first = await reminder.process_due(bot, now)
    second = await reminder.process_due(bot, now)
    assert first >= 1
    assert second == 0


@pytest.mark.asyncio
async def test_missed_reminder_not_spammed(session_factory):
    with session_scope(session_factory) as session:
        service = HabitService(session)
        service.register_or_get_user(1, None, None)

    reminder = ReminderService(session_factory, grace_minutes=10, catchup_minutes=30)
    bot = FakeBot()
    # More than catch-up window after morning 08:00
    sent = await reminder.process_due(bot, datetime(2026, 1, 10, 9, 0, tzinfo=UTC))
    assert sent == 0
