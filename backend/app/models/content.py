from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, enum_col
from app.models.enums import (
    ContentCategory,
    Difficulty,
    MockType,
    QuestionSource,
    QuestionType,
)

# ---- Global learning content: docs, questions, flashcards, mock templates, achievements ----


class ContentDocument(Base):
    """A GATE-DA-2027 narrative doc made dynamic (rendered as an in-app reference page)."""

    __tablename__ = "content_documents"

    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[ContentCategory] = mapped_column(enum_col(ContentCategory), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_md: Mapped[str] = mapped_column(Text, nullable=False)
    source_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class Question(Base):
    __tablename__ = "questions"

    topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type: Mapped[QuestionType] = mapped_column(enum_col(QuestionType), nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(enum_col(Difficulty), default=Difficulty.MEDIUM, nullable=False)
    source: Mapped[QuestionSource] = mapped_column(enum_col(QuestionSource), default=QuestionSource.PRACTICE, nullable=False)
    source_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    question_md: Mapped[str] = mapped_column(Text, nullable=False)
    explanation_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    # For NAT questions (no options); MCQ/MSQ correctness lives in question_options.
    correct_value: Mapped[str | None] = mapped_column(String(128), nullable=True)
    marks: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    negative_marks: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    expected_time_seconds: Mapped[int] = mapped_column(Integer, default=120, nullable=False)
    tags: Mapped[list | None] = mapped_column(JSONB, nullable=True)


class QuestionOption(Base):
    __tablename__ = "question_options"

    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    label: Mapped[str | None] = mapped_column(String(8), nullable=True)
    option_md: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Flashcard(Base):
    __tablename__ = "flashcards"

    topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    front_md: Mapped[str] = mapped_column(Text, nullable=False)
    back_md: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Difficulty | None] = mapped_column(enum_col(Difficulty), nullable=True)
    hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(128), nullable=True)


class MockTemplate(Base):
    """A reusable mock paper definition (global); a user's run is an `attempts` row."""

    __tablename__ = "mock_templates"

    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    mock_type: Mapped[MockType] = mapped_column(enum_col(MockType), default=MockType.FULL_SYLLABUS, nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_marks: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=180, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class MockTemplateQuestion(Base):
    __tablename__ = "mock_template_questions"
    __table_args__ = (
        UniqueConstraint("mock_template_id", "question_id"),
    )

    mock_template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mock_templates.id", ondelete="CASCADE"), index=True, nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    section: Mapped[str | None] = mapped_column(String(128), nullable=True)


class Achievement(Base):
    __tablename__ = "achievements"

    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tier: Mapped[str | None] = mapped_column(String(32), nullable=True)
    criteria: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
