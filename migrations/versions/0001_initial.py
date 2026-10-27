"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-10-27
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("timezone", sa.String(length=100), nullable=False, server_default="UTC"),
        sa.Column("paused_reminders", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("morning_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("afternoon_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("evening_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("morning_time", sa.Time(), nullable=False),
        sa.Column("afternoon_time", sa.Time(), nullable=False),
        sa.Column("evening_time", sa.Time(), nullable=False),
        sa.Column("quiet_hours_start", sa.Time(), nullable=True),
        sa.Column("quiet_hours_end", sa.Time(), nullable=True),
        sa.Column("weekly_report_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_telegram_user_id", "users", ["telegram_user_id"], unique=False)

    op.create_table(
        "habits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("daily_target", sa.Numeric(10, 2), nullable=False, server_default="1"),
        sa.Column("target_unit", sa.String(length=32), nullable=False, server_default="times"),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "key", name="uq_habits_user_key"),
    )
    op.create_index("ix_habits_user_id", "habits", ["user_id"], unique=False)

    op.create_table(
        "habit_completions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("habit_id", sa.Integer(), sa.ForeignKey("habits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False, server_default="1"),
        sa.Column("completion_key", sa.String(length=100), nullable=False, server_default="daily"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "habit_id", "local_date", "completion_key", name="uq_completion_once_slot"),
    )
    op.create_index("ix_completion_user_date", "habit_completions", ["user_id", "local_date"], unique=False)

    op.create_table(
        "reminder_deliveries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reminder_type", sa.String(length=30), nullable=False),
        sa.Column("intended_local_date", sa.Date(), nullable=False),
        sa.Column("intended_local_time", sa.Time(), nullable=False),
        sa.Column("intended_utc_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idempotency_key", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_reminder_idempotency"),
    )
    op.create_index("ix_reminder_deliveries_user_id", "reminder_deliveries", ["user_id"], unique=False)
    op.create_index(
        "ix_reminder_user_type_date",
        "reminder_deliveries",
        ["user_id", "reminder_type", "intended_local_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_reminder_user_type_date", table_name="reminder_deliveries")
    op.drop_index("ix_reminder_deliveries_user_id", table_name="reminder_deliveries")
    op.drop_table("reminder_deliveries")
    op.drop_index("ix_completion_user_date", table_name="habit_completions")
    op.drop_table("habit_completions")
    op.drop_index("ix_habits_user_id", table_name="habits")
    op.drop_table("habits")
    op.drop_index("ix_users_telegram_user_id", table_name="users")
    op.drop_table("users")
