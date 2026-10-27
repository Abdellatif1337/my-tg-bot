from __future__ import annotations

from datetime import UTC, datetime

from telegram import Update
from telegram.ext import ContextTypes

from app.database import session_scope
from app.handlers.common import is_authorized, reject_unauthorized
from app.services.habit_service import HabitService
from app.services.stats_service import StatsService


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = context.application.bot_data["settings"]
    if not is_authorized(update, settings.admin_telegram_ids):
        await reject_unauthorized(update)
        return

    tg_user = update.effective_user
    session_factory = context.application.bot_data["session_factory"]
    with session_scope(session_factory) as session:
        habits = HabitService(session)
        user = habits.get_user_by_telegram_id(tg_user.id)
        if not user:
            await update.effective_message.reply_text("Use /start first.")
            return
        stats = StatsService(session).summary(user, datetime.now(tz=UTC))

    text = (
        "DisciplineOS stats\n\n"
        f"Today: {stats.today_completed}/{stats.today_total} ({stats.today_percent}%)\n"
        f"This week: {stats.weekly_percent}%\n"
        f"Current streak: {stats.current_streak} day(s)\n"
        f"Best streak: {stats.best_streak} day(s)"
    )
    await update.effective_message.reply_text(text)
