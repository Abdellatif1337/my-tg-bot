from __future__ import annotations

import os

import pytest

from app.config import ConfigError, Settings


def test_config_requires_secret_env(monkeypatch):
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    monkeypatch.setenv("DATABASE_URL", "******localhost/db")
    monkeypatch.setenv("ADMIN_TELEGRAM_ID", "1")
    with pytest.raises(ConfigError):
        Settings.from_env()


def test_config_parses_admin_ids(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "token")
    monkeypatch.setenv("DATABASE_URL", "******localhost/db")
    monkeypatch.setenv("ADMIN_TELEGRAM_ID", "1,2")
    settings = Settings.from_env()
    assert settings.admin_telegram_ids == {1, 2}
