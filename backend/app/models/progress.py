from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, enum_col
from app.models.enums import ProgressStatus, RevisionStatus, SessionType

# ---- Per-user progress: topic status, study sessions, revision ladder, flashcard state ----


class UserTopicProgress(Base):
    __tablename__ = "user_topic_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    status: Mapped[ProgressStatus] = mapped_column(
        enum_col(ProgressStatus), default=ProgressStatus.NOT_STARTED, nullable=False
    )
    completion_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    retention_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    accuracy_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    pyqs_solved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    practice_solved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    revision_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_studied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_revised_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class StudySession(Base):
    __tablename__ = "study_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("topics.id", ondelete="SET NULL"), index=True, nullable=True
    )
    session_type: Mapped[SessionType] = mapped_column(
        enum_col(SessionType), default=SessionType.LEARNING, nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Focus-session metadata (an active session has ended_at IS NULL until stopped).
    interruptions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    focus_score: Mapped[int | None] = mapped_column(Integer, nullable=True)


class RevisionSchedule(Base):
    """One row per (user, topic, ladder step) — the 1/3/7/15/30/60/90-day spaced-repetition ladder."""

    __tablename__ = "revision_schedules"
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", "interval_day"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    interval_day: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    status: Mapped[RevisionStatus] = mapped_column(
        enum_col(RevisionStatus), default=RevisionStatus.PENDING, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UserFlashcard(Base):
    """Per-user Leitner state for a flashcard."""

    __tablename__ = "user_flashcards"
    __table_args__ = (
        UniqueConstraint("user_id", "flashcard_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    flashcard_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("flashcards.id", ondelete="CASCADE"), index=True, nullable=False
    )
    box: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    ease: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    times_reviewed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    times_correct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    review_later: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class UserResource(Base):
    """Per-user state for a learning resource: favorite, completion, watch progress, rating, notes."""

    __tablename__ = "user_resources"
    __table_args__ = (
        UniqueConstraint("user_id", "resource_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"), index=True, nullable=False
    )
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    watch_progress_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
