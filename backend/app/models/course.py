from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import ResourceLevel

if TYPE_CHECKING:
    from app.models.user import User


class Course(Base):
    """Multi-lesson course catalog entry (NPTEL course, Coursera specialization, etc.)."""

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    platform: Mapped[str] = mapped_column(String(120), nullable=False)
    instructor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    level: Mapped[ResourceLevel] = mapped_column(Enum(ResourceLevel), default=ResourceLevel.BEGINNER, nullable=False)
    is_free: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    lessons: Mapped[list["CourseLesson"]] = relationship(back_populates="course", cascade="all, delete-orphan", order_by="CourseLesson.order_index")
    user_progress: Mapped[list["UserCourseProgress"]] = relationship(back_populates="course", cascade="all, delete-orphan")


class CourseLesson(Base):
    __tablename__ = "course_lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    video_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    course: Mapped["Course"] = relationship(back_populates="lessons")


class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    current_lesson_id: Mapped[int | None] = mapped_column(ForeignKey("course_lessons.id", ondelete="SET NULL"), nullable=True)
    completed_lessons_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    percent_complete: Mapped[float] = mapped_column(default=0.0, nullable=False)
    is_bookmarked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_resumed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="course_progress")
    course: Mapped["Course"] = relationship(back_populates="user_progress")
