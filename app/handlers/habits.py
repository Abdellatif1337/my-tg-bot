from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes

from app.database import session_scope
from app.handlers.common import is_authorized, reject_unauthorized
from app.keyboards import habits_keyboard, today_keyboard
from app.messages import TODAY_HEADER
from app.services.habit_service import HabitService


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = context.application.bot_data["settings"]
    if not is_authorized(update, settings.admin_telegram_ids):
        await reject_unauthorized(update)
        return

    tg_user = update.effective_user
    if not tg_user:
        return

    now_utc = datetime.now(tz=UTC)
    session_factory = context.application.bot_data["session_factory"]
    with session_scope(session_factory) as session:
        service = HabitService(session)
        user = service.get_user_by_telegram_id(tg_user.id)
        if not user:
            await update.effective_message.reply_text("Use /start first.")
            return

        habits = service.get_habits(user.id, enabled_only=True)
        progress = service.today_progress(user, now_utc)
        text = (
            f"{TODAY_HEADER}\n\n"
            f"Completed: {progress.completed_habits} / {progress.total_habits}\n"
            f"Progress: {progress.percent}%"
        )

    await update.effective_message.reply_text(text, reply_markup=today_keyboard(habits))


async def habits_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        habits = service.get_habits(user.id)

    lines = [f"{'✅' if h.enabled else '⏸️'} {h.name} ({h.key}) target: {h.daily_target} {h.target_unit}" for h in habits]
    await update.effective_message.reply_text("Your habits:\n" + "\n".join(lines), reply_markup=habits_keyboard(habits))


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = context.application.bot_data["settings"]
    if not is_authorized(update, settings.admin_telegram_ids):
        await reject_unauthorized(update)
        return
    await today_command(update, context)


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    settings = context.application.bot_data["settings"]
    if not is_authorized(update, settings.admin_telegram_ids):
        await query.edit_message_text("Unauthorized action.")
        return

    parts = (query.data or "").split(":")
    if len(parts) < 3:
        await query.edit_message_text("Invalid action.")
        return

    action, sub_action, habit_key = parts[0], parts[1], parts[2]
    if action not in {"habit", "water", "prayer"}:
        await query.edit_message_text("Invalid action.")
        return

    tg_user = update.effective_user
    now_utc = datetime.now(tz=UTC)
    session_factory = context.application.bot_data["session_factory"]
    with session_scope(session_factory) as session:
        service = HabitService(session)
        user = service.get_user_by_telegram_id(tg_user.id)
        if not user:
            await query.edit_message_text("Use /start first.")
            return

        if action == "habit":
            if sub_action == "done":
                marked = service.mark_completion(user, habit_key, now_utc)
                await query.edit_message_text("Habit marked complete." if marked else "Already completed today.")
                return
            if sub_action == "undo":
                removed = service.undo_daily_completion(user, habit_key, now_utc)
                await query.edit_message_text("Completion removed." if removed else "Nothing to undo.")
                return
            if sub_action == "toggle":
                habit = service.toggle_habit(user.id, habit_key)
                if habit:
                    await query.edit_message_text(
                        f"{habit.name} is now {'enabled' if habit.enabled else 'disabled'}."
                    )
                else:
                    await query.edit_message_text("Habit not found.")
                return
            if sub_action == "progress":
                habits = {habit.key: habit for habit in service.get_habits(user.id)}
                habit = habits.get(habit_key)
                if not habit:
                    await query.edit_message_text("Habit not found.")
                    return
                if habit_key == "water":
                    consumed, remaining = service.water_status(user, now_utc)
                    await query.edit_message_text(f"Water: {consumed} ml, remaining {remaining} ml.")
                    return
                await query.edit_message_text("Use /stats for detailed progress.")
                return

        if action == "water" and sub_action == "add":
            try:
                amount = Decimal(habit_key)
            except Exception:
                await query.edit_message_text("Invalid water amount.")
                return
            service.mark_completion(user, "water", now_utc, quantity=amount)
            consumed, remaining = service.water_status(user, now_utc)
            await query.edit_message_text(f"Logged {amount} ml. Total today: {consumed} ml. Remaining: {remaining} ml.")
            return

        if action == "prayer" and sub_action == "add":
            service.mark_completion(user, "prayer", now_utc, quantity=Decimal("1"), completion_key=f"prayer-{now_utc.isoformat()}")
            await query.edit_message_text("Prayer entry logged.")
            return

    await query.edit_message_text("Unknown action.")
