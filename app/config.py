from __future__ import annotations

import os
from dataclasses import dataclass
from typing import FrozenSet


class ConfigError(ValueError):
    """Raised when required configuration is missing or invalid."""


def _parse_admin_ids(raw: str) -> FrozenSet[int]:
    if not raw:
        raise ConfigError("ADMIN_TELEGRAM_ID is required")
    values: set[int] = set()
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            values.add(int(item))
        except ValueError as exc:
            raise ConfigError("ADMIN_TELEGRAM_ID must contain integer values") from exc
    if not values:
        raise ConfigError("ADMIN_TELEGRAM_ID is required")
    return frozenset(values)


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str
    admin_telegram_ids: FrozenSet[int]
    default_timezone: str = "UTC"
    log_level: str = "INFO"
    reminder_poll_seconds: int = 60
    reminder_send_grace_minutes: int = 10
    reminder_catchup_minutes: int = 30


    @staticmethod
    def from_env() -> "Settings":
        bot_token = os.getenv("BOT_TOKEN", "").strip()
        database_url = os.getenv("DATABASE_URL", "").strip()
        if not bot_token:
            raise ConfigError("BOT_TOKEN is required")
        if not database_url:
            raise ConfigError("DATABASE_URL is required")

        admin_ids = _parse_admin_ids(os.getenv("ADMIN_TELEGRAM_ID", ""))

        poll_seconds = int(os.getenv("REMINDER_POLL_SECONDS", "60"))
        if poll_seconds <= 0:
            raise ConfigError("REMINDER_POLL_SECONDS must be positive")

        return Settings(
            bot_token=bot_token,
            database_url=database_url,
            admin_telegram_ids=admin_ids,
            default_timezone=os.getenv("DEFAULT_TIMEZONE", "UTC").strip() or "UTC",
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            reminder_poll_seconds=poll_seconds,
            reminder_send_grace_minutes=int(os.getenv("REMINDER_SEND_GRACE_MINUTES", "10")),
            reminder_catchup_minutes=int(os.getenv("REMINDER_CATCHUP_MINUTES", "30")),
        )
