from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, SoftDeleteMixin, enum_col
from app.models.enums import (
    AiRole,
    AttemptStatus,
    AttemptType,
    BookmarkType,
    FileKind,
    MistakeCategory,
    ReminderType,
)

# ---- Per-user activity: attempts, notes, bookmarks, mistakes, analytics, AI chats, files ----


class Attempt(Base):
    """A practice set OR a mock run. `mock_template_id` distinguishes mocks."""

    __tablename__ = "attempts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    attempt_type: Mapped[AttemptType] = mapped_column(enum_col(AttemptType), nullable=False)
    mock_template_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("mock_templates.id", ondelete="SET NULL"), index=True, nullable=True
    )
    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("topics.id", ondelete="SET NULL"), nullable=True
    )
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[AttemptStatus] = mapped_column(
        enum_col(AttemptStatus), default=AttemptStatus.IN_PROGRESS, nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    accuracy_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    correct_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    incorrect_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    negative_marks_lost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    predicted_gate_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("attempts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    selected_option_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    nat_value: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_skipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    marks_awarded: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    time_taken_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Note(Base, SoftDeleteMixin):
    __tablename__ = "notes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("topics.id", ondelete="SET NULL"), index=True, nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_md: Mapped[str] = mapped_column(Text, default="", nullable=False)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Bookmark(Base, SoftDeleteMixin):
    """Polymorphic bookmark: `target_type` + `target_id` point at any entity (resolved live)."""

    __tablename__ = "bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    target_type: Mapped[BookmarkType] = mapped_column(enum_col(BookmarkType), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class Mistake(Base):
    """Error-notebook entry (from ERROR_NOTEBOOK + live wrong answers)."""

    __tablename__ = "mistakes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("topics.id", ondelete="SET NULL"), index=True, nullable=True
    )
    question_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("questions.id", ondelete="SET NULL"), nullable=True
    )
    attempt_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("attempts.id", ondelete="SET NULL"), nullable=True
    )
    category: Mapped[MistakeCategory] = mapped_column(enum_col(MistakeCategory), nullable=False)
    description_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AnalyticsSnapshot(Base):
    """Daily rollup: predicted score/AIR, per-subject accuracy, weak/strong topics."""

    __tablename__ = "analytics_snapshots"
    __table_args__ = (
        UniqueConstraint("user_id", "snapshot_date"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    predicted_marks: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_air: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    per_subject_accuracy: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    weak_topics: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    strong_topics: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    study_minutes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class AiConversation(Base, SoftDeleteMixin):
    __tablename__ = "ai_conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), default="New chat", nullable=False)


class AiMessage(Base):
    __tablename__ = "ai_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ai_conversations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role: Mapped[AiRole] = mapped_column(enum_col(AiRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Snapshot of the user-data context injected for this turn (for auditability).
    context_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class File(Base, SoftDeleteMixin):
    """Cloudinary-backed uploads (avatars, attachments, exported AI notes)."""

    __tablename__ = "files"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    kind: Mapped[FileKind] = mapped_column(enum_col(FileKind), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    public_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    filename: Mapped[str | None] = mapped_column(String(512), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE"), index=True, nullable=False
    )
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class Reminder(Base):
    __tablename__ = "reminders"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    reminder_type: Mapped[ReminderType] = mapped_column(enum_col(ReminderType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
