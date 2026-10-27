from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.models import Habit


def today_keyboard(habits: list[Habit]) -> InlineKeyboardMarkup:
    rows = []
    for habit in habits:
        rows.append(
            [
                InlineKeyboardButton(f"✅ {habit.name}", callback_data=f"habit:done:{habit.key}"),
                InlineKeyboardButton(f"↩️ {habit.name}", callback_data=f"habit:undo:{habit.key}"),
            ]
        )
        rows.append(
            [
                InlineKeyboardButton("📊", callback_data=f"habit:progress:{habit.key}"),
                InlineKeyboardButton("⚙️", callback_data=f"habit:toggle:{habit.key}"),
            ]
        )
    rows.append([InlineKeyboardButton("Log Water +250ml", callback_data="water:add:250")])
    rows.append([InlineKeyboardButton("Prayer done", callback_data="prayer:add:1")])
    return InlineKeyboardMarkup(rows)


def habits_keyboard(habits: list[Habit]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(f"{'🟢' if habit.enabled else '⚫'} {habit.name}", callback_data=f"habit:toggle:{habit.key}")]
        for habit in habits
    ]
    return InlineKeyboardMarkup(rows)
