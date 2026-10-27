from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.database import session_scope
from app.handlers.common import is_authorized, reject_unauthorized
from app.messages import HELP_MESSAGE, WELCOME_MESSAGE
from app.services.habit_service import HabitService


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = context.application.bot_data["settings"]
    if not is_authorized(update, settings.admin_telegram_ids):
        await reject_unauthorized(update)
        return

    tg_user = update.effective_user
    if not tg_user:
        return
    session_factory = context.application.bot_data["session_factory"]
    with session_scope(session_factory) as session:
        service = HabitService(session)
        service.register_or_get_user(
            telegram_user_id=tg_user.id,
            username=tg_user.username,
            display_name=tg_user.full_name,
            timezone=settings.default_timezone,
        )

    await update.effective_message.reply_text(WELCOME_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = context.application.bot_data["settings"]
    if not is_authorized(update, settings.admin_telegram_ids):
        await reject_unauthorized(update)
        return
    await update.effective_message.reply_text(HELP_MESSAGE)
