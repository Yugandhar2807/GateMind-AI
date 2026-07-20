from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import Difficulty, QuestionSource, QuestionType

if TYPE_CHECKING:
    from app.models.content import Topic


class Question(Base):
    """
    Unified question bank entry for PYQs, generated practice, and mock-test pools.
    `options` holds an ordered JSON list for MCQ/MSQ; `correct_answer` holds either
    an option index/list (MCQ/MSQ) or a numeric string with tolerance (NAT).
    """

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)

    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), nullable=False)
    source: Mapped[QuestionSource] = mapped_column(Enum(QuestionSource), nullable=False)
    source_year: Mapped[int | None] = mapped_column(Integer, nullable=True)  # e.g. 2025 for a PYQ

    question_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list | None] = mapped_column(JSON, nullable=True)
    correct_answer: Mapped[dict] = mapped_column(JSON, nullable=False)
    nat_tolerance: Mapped[float | None] = mapped_column(Float, nullable=True)
    explanation_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)

    marks: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    negative_marks: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    expected_time_seconds: Mapped[int] = mapped_column(Integer, default=90, nullable=False)

    topic: Mapped["Topic"] = relationship(back_populates="questions")
