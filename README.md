# DisciplineOS

DisciplineOS is a production-oriented Telegram habit reminder bot with PostgreSQL persistence, timezone-aware reminders, inline button interactions, and statistics/streak tracking.

## Architecture

- `app/main.py`: application bootstrap and handler registration.
- `app/config.py`: startup configuration validation from env vars.
- `app/database.py`: SQLAlchemy engine/session management.
- `app/models.py`: database models for users, habits, completions, reminder deliveries.
- `app/handlers/*`: Telegram command and callback handlers.
- `app/services/*`: business logic for habits, reminders, and statistics.
- `app/scheduler.py`: scheduler abstraction (APScheduler backend).
- `migrations/`: Alembic migration scripts.
- `tests/`: automated tests.

## Telegram setup with BotFather

1. Open Telegram and chat with `@BotFather`.
2. Run `/newbot` and follow prompts.
3. Copy the bot token and keep it private.
4. To rotate a leaked token: run `/revoke` then generate a new token with `/token` and update env vars.

## Configure bot commands in Telegram

Commands are also set programmatically on startup. Manual BotFather fallback:

```
start - Initialize your profile
today - Show today's mission
habits - Manage habits
done - Mark a habit done
stats - Show stats and streaks
settings - Show settings
pause - Pause reminders
resume - Resume reminders
help - Show help
```

## Android / GitHub web workflow

1. Create the repository from GitHub mobile/web.
2. Open Codespaces or use Copilot coding agent from GitHub UI.
3. Add secrets via repository/environment settings (never commit `.env`).
4. Review CI status from the Actions tab on mobile.

## Environment variables

Copy `.env.example` to `.env` for local development:

- `BOT_TOKEN`
- `DATABASE_URL`
- `ADMIN_TELEGRAM_ID` (single ID or comma-separated IDs)
- `DEFAULT_TIMEZONE`
- `LOG_LEVEL`
- `REMINDER_POLL_SECONDS`
- `REMINDER_SEND_GRACE_MINUTES`
- `REMINDER_CATCHUP_MINUTES`

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.main
```

## Migrations

- Initialize DB schema: `alembic upgrade head`
- Create new migration: `alembic revision --autogenerate -m "message"`

## Deploy on Render (worker + PostgreSQL)

1. Create a new Render Blueprint and point to `render.yaml`, or create worker/db manually.
2. Set env vars: `BOT_TOKEN`, `ADMIN_TELEGRAM_ID`, and `DATABASE_URL`.
3. Build uses Dockerfile; start command is `python -m app.main`.
4. Run migrations in a Render shell before first start:
   - `alembic upgrade head`
5. Keep a single worker instance to avoid polling conflicts.

### Cost / free tier notes

Render free tiers and sleep behavior change over time. Verify current pricing and always-on worker limits directly in Render’s current pricing page before relying on continuous reminders.

## Reminders and catch-up policy

- Default windows: 08:00, 14:00, 20:00 (user-local time).
- User timezone stored in DB (default UTC until changed).
- Reminder sends only inside the grace window and never beyond catch-up limit.
- Missed reminders are not replayed in bulk after downtime.
- `reminder_deliveries.idempotency_key` prevents duplicate sends after restart/retry.

Manual verification without waiting:
- Set `REMINDER_POLL_SECONDS=10` and temporarily set reminder times close to current local time.
- Start bot and watch logs/messages.

## Security

- Credentials are read only from env vars.
- `.env` is gitignored.
- Unauthorized Telegram users are blocked.
- Callback data is validated before action routing.
- No token/DB credentials are logged intentionally.

## Commands

- `/start` register owner profile and default habits.
- `/today` daily mission summary + inline actions.
- `/habits` list habits with enable/disable controls.
- `/done` shortcut to today view/actions.
- `/stats` daily/weekly stats + streaks.
- `/settings` view reminder and timezone settings.
- `/settings_timezone <IANA>` set timezone.
- `/pause` and `/resume` reminder controls.

## Testing

```bash
pytest -q
```

Coverage includes registration, authorization config validation, duplicate completion protection, water/prayer tracking, streak/statistics, reminder idempotency, and missed-reminder policy.

## Logs, troubleshooting, recovery

- Inspect worker logs in Render dashboard.
- If bot stops sending reminders: verify worker is running, `BOT_TOKEN` valid, DB reachable, and `paused_reminders` state.
- After restart, scheduler reconstructs due checks from persisted user settings and uses delivery idempotency to avoid duplicates.

## Safe updates

1. Pull latest code.
2. Run tests locally/CI.
3. Apply migrations: `alembic upgrade head`.
4. Deploy worker.
5. Confirm `/today` and reminder flow.

## Backup and restore

- Use managed PostgreSQL daily backups (provider feature).
- Test restore into staging before production rollback.
- Preserve migration history to keep schema compatible.
