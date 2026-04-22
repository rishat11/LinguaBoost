"""sqlite initial schema

Revision ID: 202604231500
Revises:
Create Date: 2026-04-23

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import JSON, Uuid

revision: str = "202604231500"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "telegram_processed_updates",
        sa.Column("update_id", sa.BigInteger(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("update_id"),
    )
    op.create_table(
        "users",
        sa.Column("id", Uuid(as_uuid=True), nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_username", sa.Text(), nullable=True),
        sa.Column("ui_locale", sa.String(length=16), server_default="ru", nullable=False),
        sa.Column("target_language", sa.String(length=16), server_default="en", nullable=False),
        sa.Column("level", sa.String(length=16), server_default="A1", nullable=False),
        sa.Column("timezone", sa.String(length=64), server_default="Europe/Moscow", nullable=False),
        sa.Column("onboarding_step", sa.String(length=32), nullable=True),
        sa.Column("onboarding_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reminders_enabled", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("reminder_local_time", sa.Time(), nullable=True),
        sa.Column("quiet_hours_start", sa.Time(), nullable=True),
        sa.Column("quiet_hours_end", sa.Time(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_user_id"),
    )
    op.create_table(
        "user_deletion_requests",
        sa.Column("id", Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", Uuid(as_uuid=True), nullable=False),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "lesson_progress",
        sa.Column("id", Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", Uuid(as_uuid=True), nullable=False),
        sa.Column("content_pack_version", sa.String(length=64), nullable=False),
        sa.Column("lesson_id", sa.String(length=128), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("state", JSON(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "content_pack_version",
            "local_date",
            name="uq_lesson_progress_user_pack_day",
        ),
    )
    op.create_index(
        "ix_lesson_progress_user_local_date",
        "lesson_progress",
        ["user_id", "local_date"],
        unique=False,
    )
    op.create_table(
        "practice_sessions",
        sa.Column("id", Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", Uuid(as_uuid=True), nullable=False),
        sa.Column("scenario_id", sa.String(length=128), nullable=False),
        sa.Column("state_machine_state", sa.String(length=128), nullable=False),
        sa.Column("context", JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_practice_sessions_user_open",
        "practice_sessions",
        ["user_id"],
        unique=False,
        sqlite_where=sa.text("completed_at IS NULL"),
    )
    op.create_table(
        "user_stats",
        sa.Column("user_id", Uuid(as_uuid=True), nullable=False),
        sa.Column("streak_current", sa.Integer(), server_default="0", nullable=False),
        sa.Column("streak_best", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lessons_completed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_activity_local_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_stats")
    op.drop_index("ix_practice_sessions_user_open", table_name="practice_sessions")
    op.drop_table("practice_sessions")
    op.drop_index("ix_lesson_progress_user_local_date", table_name="lesson_progress")
    op.drop_table("lesson_progress")
    op.drop_table("user_deletion_requests")
    op.drop_table("users")
    op.drop_table("telegram_processed_updates")
