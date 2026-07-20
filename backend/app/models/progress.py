from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import ProgressStatus, SessionType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.content import Topic


class UserTopicProgress(Base):
    """One row per (user, topic): the live rollup shown on the roadmap and dashboard."""

    __tablename__ = "user_topic_progress"
    __table_args__ = (UniqueConstraint("user_id", "topic_id", name="uq_user_topic_progress"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)

    status: Mapped[ProgressStatus] = mapped_column(Enum(ProgressStatus), default=ProgressStatus.NOT_STARTED, nullable=False)
    completion_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    retention_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    accuracy_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    pyqs_solved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    practice_solved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    revision_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_studied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_revised_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="topic_progress")
    topic: Mapped["Topic"] = relationship(back_populates="progress_entries")


class StudySession(Base):
    """A logged block of study time — the raw material behind streaks/heatmaps/analytics."""

    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True)

    session_type: Mapped[SessionType] = mapped_column(Enum(SessionType), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="study_sessions")
