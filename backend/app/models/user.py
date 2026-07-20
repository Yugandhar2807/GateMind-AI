from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, Float, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import PreferredStudyTime, UserRole

if TYPE_CHECKING:
    from app.models.progress import UserTopicProgress, StudySession
    from app.models.mock import QuizAttempt
    from app.models.bookmark import Bookmark
    from app.models.flashcard import UserFlashcard
    from app.models.mistake import Mistake
    from app.models.note import Note
    from app.models.reminder import Reminder
    from app.models.revision import RevisionSchedule
    from app.models.analytics import AnalyticsSnapshot
    from app.models.course import UserCourseProgress


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)

    # Profile
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    target_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_air: Mapped[int | None] = mapped_column(Integer, nullable=True)
    daily_study_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    preferred_study_time: Mapped[PreferredStudyTime | None] = mapped_column(
        Enum(PreferredStudyTime), nullable=True
    )
    exam_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gym_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Streak tracking (denormalized for fast dashboard reads; recomputed by scheduler)
    current_streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    topic_progress: Mapped[list["UserTopicProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    study_sessions: Mapped[list["StudySession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    bookmarks: Mapped[list["Bookmark"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    flashcards: Mapped[list["UserFlashcard"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    mistakes: Mapped[list["Mistake"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notes: Mapped[list["Note"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    revision_schedules: Mapped[list["RevisionSchedule"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    analytics_snapshots: Mapped[list["AnalyticsSnapshot"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    course_progress: Mapped[list["UserCourseProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
