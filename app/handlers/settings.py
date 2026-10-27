from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.database import session_scope
from app.handlers.common import is_authorized, reject_unauthorized
from app.services.habit_service import HabitService


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = context.application.bot_data["settings"]
    if not is_authorized(update, settings.admin_telegram_ids):
        await reject_unauthorized(update)
        return

    tg_user = update.effective_user
    session_factory = context.application.bot_data["session_factory"]
    with session_scope(session_factory) as session:
        service = HabitService(session)
        user = service.get_user_by_telegram_id(tg_user.id)
        if not user:
            await update.effective_message.reply_text("Use /start first.")
            return

        text = (
            f"Timezone: {user.timezone}\n"
            f"Paused reminders: {user.paused_reminders}\n"
            f"Morning: {'on' if user.morning_enabled else 'off'} at {user.morning_time}\n"
            f"Afternoon: {'on' if user.afternoon_enabled else 'off'} at {user.afternoon_time}\n"
            f"Evening: {'on' if user.evening_enabled else 'off'} at {user.evening_time}\n"
            "To set timezone use: /settings_timezone <IANA timezone>."
        )
    await update.effective_message.reply_text(text)


async def settings_timezone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = context.application.bot_data["settings"]
    if not is_authorized(update, settings.admin_telegram_ids):
        await reject_unauthorized(update)
        return
    if not context.args:
        await update.effective_message.reply_text("Usage: /settings_timezone <IANA timezone>")
        return

    timezone = context.args[0]
    from zoneinfo import ZoneInfo

    try:
        ZoneInfo(timezone)
    except Exception:
        await update.effective_message.reply_text("Invalid timezone. Example: Europe/Berlin")
        return

    tg_user = update.effective_user
    session_factory = context.application.bot_data["session_factory"]
    with session_scope(session_factory) as session:
        service = HabitService(session)
        user = service.get_user_by_telegram_id(tg_user.id)
        if not user:
            await update.effective_message.reply_text("Use /start first.")
            return
        user.timezone = timezone

    await update.effective_message.reply_text(f"Timezone updated to {timezone}.")


async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _set_pause_state(update, context, True)


async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _set_pause_state(update, context, False)


async def _set_pause_state(update: Update, context: ContextTypes.DEFAULT_TYPE, pause: bool) -> None:
    settings = context.application.bot_data["settings"]
    if not is_authorized(update, settings.admin_telegram_ids):
        await reject_unauthorized(update)
        return
    tg_user = update.effective_user
    session_factory = context.application.bot_data["session_factory"]
    with session_scope(session_factory) as session:
        service = HabitService(session)
        user = service.get_user_by_telegram_id(tg_user.id)
        if not user:
            await update.effective_message.reply_text("Use /start first.")
            return
        user.paused_reminders = pause

    await update.effective_message.reply_text("Reminders paused." if pause else "Reminders resumed.")
