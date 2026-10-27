from __future__ import annotations

from telegram import Update

from app.messages import UNAUTHORIZED_MESSAGE


def is_authorized(update: Update, admin_ids: set[int] | frozenset[int]) -> bool:
    user = update.effective_user
    return bool(user and user.id in admin_ids)


async def reject_unauthorized(update: Update) -> None:
    message = update.effective_message
    if message:
        await message.reply_text(UNAUTHORIZED_MESSAGE)
