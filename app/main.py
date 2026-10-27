from __future__ import annotations

import logging
from datetime import UTC, datetime

from telegram import BotCommand, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from app.config import ConfigError, Settings
from app.database import create_session_factory
from app.handlers.habits import callback_router, done_command, habits_command, today_command
from app.handlers.settings import pause_command, resume_command, settings_command, settings_timezone_command
from app.handlers.start import help_command, start_command
from app.handlers.stats import stats_command
from app.scheduler import APSchedulerBackend
from app.services.reminder_service import ReminderService

LOGGER = logging.getLogger(__name__)


async def _set_commands(application: Application) -> None:
    commands = [
        BotCommand("start", "Initialize your profile"),
        BotCommand("today", "Show today's mission"),
        BotCommand("habits", "Manage habits"),
        BotCommand("done", "Mark a habit done"),
        BotCommand("stats", "Show stats and streaks"),
        BotCommand("settings", "Show settings"),
        BotCommand("pause", "Pause reminders"),
        BotCommand("resume", "Resume reminders"),
        BotCommand("help", "Show help"),
    ]
    await application.bot.set_my_commands(commands)


async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    LOGGER.exception("Unhandled Telegram error", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text("An internal error happened. Please try again.")


def build_application(settings: Settings) -> Application:
    session_factory = create_session_factory(settings.database_url)
    app = Application.builder().token(settings.bot_token).build()
    app.bot_data["settings"] = settings
    app.bot_data["session_factory"] = session_factory

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("habits", habits_command))
    app.add_handler(CommandHandler("done", done_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("settings_timezone", settings_timezone_command))
    app.add_handler(CommandHandler("pause", pause_command))
    app.add_handler(CommandHandler("resume", resume_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_error_handler(_error_handler)

    reminder_service = ReminderService(
        session_factory,
        grace_minutes=settings.reminder_send_grace_minutes,
        catchup_minutes=settings.reminder_catchup_minutes,
    )
    backend = APSchedulerBackend()

    async def reminder_tick() -> None:
        await reminder_service.process_due(app.bot, now_utc=datetime.now(tz=UTC))

    backend.add_interval_job(reminder_tick, settings.reminder_poll_seconds, "disciplineos-reminders")
    backend.start()
    app.bot_data["scheduler_backend"] = backend

    async def on_shutdown(_: Application) -> None:
        backend.shutdown()

    app.post_init = _set_commands
    app.post_shutdown = on_shutdown
    return app


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        raise SystemExit(str(exc)) from exc

    application = build_application(settings)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
