from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import MockStatus, MockType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.content import Topic
    from app.models.question import Question


class MockTest(Base):
    """A generated mock — weekly (topics completed that week), monthly, quarterly, or on demand."""

    __tablename__ = "mock_tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    mock_type: Mapped[MockType] = mapped_column(Enum(MockType), nullable=False)
    status: Mapped[MockStatus] = mapped_column(Enum(MockStatus), default=MockStatus.SCHEDULED, nullable=False)

    scheduled_for: Mapped[date] = mapped_column(Date, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=180, nullable=False)
    total_marks: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)

    questions: Mapped[list["MockTestQuestion"]] = relationship(back_populates="mock_test", cascade="all, delete-orphan", order_by="MockTestQuestion.order_index")
    attempts: Mapped[list["QuizAttempt"]] = relationship(back_populates="mock_test", cascade="all, delete-orphan")


class MockTestQuestion(Base):
    __tablename__ = "mock_test_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mock_test_id: Mapped[int] = mapped_column(ForeignKey("mock_tests.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    mock_test: Mapped["MockTest"] = relationship(back_populates="questions")
    question: Mapped["Question"] = relationship()
    topic: Mapped["Topic"] = relationship(back_populates="mock_questions")


class QuizAttempt(Base):
    """One submission of either a mock test or a standalone topic quiz."""

    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mock_test_id: Mapped[int | None] = mapped_column(ForeignKey("mock_tests.id", ondelete="CASCADE"), nullable=True, index=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True)

    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    accuracy_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_time_per_question_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    negative_marks_lost: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    lucky_guess_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    predicted_gate_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_air: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weak_topics_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    strong_topics_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="quiz_attempts")
    mock_test: Mapped["MockTest | None"] = relationship(back_populates="attempts")
    answers: Mapped[list["QuizAnswer"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)

    user_answer: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_skipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    marked_for_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    time_taken_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    marks_awarded: Mapped[float | None] = mapped_column(Float, nullable=True)

    attempt: Mapped["QuizAttempt"] = relationship(back_populates="answers")
    question: Mapped["Question"] = relationship()
