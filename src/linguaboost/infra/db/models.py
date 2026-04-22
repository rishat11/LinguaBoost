import uuid
from datetime import date, datetime, time
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Time,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from linguaboost.infra.db.base import Base


class TelegramProcessedUpdate(Base):
    """Идемпотентность webhook: один update_id — одна запись."""

    __tablename__ = "telegram_processed_updates"

    update_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    telegram_username: Mapped[str | None] = mapped_column(Text, nullable=True)
    ui_locale: Mapped[str] = mapped_column(String(16), nullable=False, server_default="ru")
    target_language: Mapped[str] = mapped_column(String(16), nullable=False, server_default="en")
    level: Mapped[str] = mapped_column(String(16), nullable=False, server_default="A1")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, server_default="Europe/Moscow")
    onboarding_step: Mapped[str | None] = mapped_column(String(32), nullable=True)
    onboarding_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reminders_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    reminder_local_time: Mapped[time | None] = mapped_column(Time(timezone=False), nullable=True)
    quiet_hours_start: Mapped[time | None] = mapped_column(Time(timezone=False), nullable=True)
    quiet_hours_end: Mapped[time | None] = mapped_column(Time(timezone=False), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    stats: Mapped["UserStats | None"] = relationship(back_populates="user", uselist=False)
    deletion_requests: Mapped[list["UserDeletionRequest"]] = relationship(back_populates="user")
    lesson_progress: Mapped[list["LessonProgress"]] = relationship(back_populates="user")
    practice_sessions: Mapped[list["PracticeSession"]] = relationship(back_populates="user")


class UserDeletionRequest(Base):
    __tablename__ = "user_deletion_requests"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="pending")

    user: Mapped["User"] = relationship(back_populates="deletion_requests")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "content_pack_version",
            "local_date",
            name="uq_lesson_progress_user_pack_day",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_pack_version: Mapped[str] = mapped_column(String(64), nullable=False)
    lesson_id: Mapped[str] = mapped_column(String(128), nullable=False)
    local_date: Mapped[date] = mapped_column(Date, nullable=False)
    state: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="lesson_progress")


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    scenario_id: Mapped[str] = mapped_column(String(128), nullable=False)
    state_machine_state: Mapped[str] = mapped_column(String(128), nullable=False)
    context: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship(back_populates="practice_sessions")


class UserStats(Base):
    __tablename__ = "user_stats"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    streak_current: Mapped[int] = mapped_column(Integer(), nullable=False, server_default="0")
    streak_best: Mapped[int] = mapped_column(Integer(), nullable=False, server_default="0")
    lessons_completed: Mapped[int] = mapped_column(Integer(), nullable=False, server_default="0")
    last_activity_local_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    user: Mapped["User"] = relationship(back_populates="stats")
