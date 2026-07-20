from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import Difficulty

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.content import Topic


class Flashcard(Base):
    """The card content itself — shared across users; per-user review state lives in UserFlashcard."""

    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    front_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    back_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), default=Difficulty.MEDIUM, nullable=False)
    is_auto_generated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    topic: Mapped["Topic"] = relationship(back_populates="flashcards")
    user_states: Mapped[list["UserFlashcard"]] = relationship(back_populates="flashcard", cascade="all, delete-orphan")


class UserFlashcard(Base):
    """
    Leitner-box style per-user review state for a flashcard.
    box 1-5: higher box = longer interval, matches the revision engine's spacing philosophy.
    """

    __tablename__ = "user_flashcards"
    __table_args__ = (UniqueConstraint("user_id", "flashcard_id", name="uq_user_flashcard"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    flashcard_id: Mapped[int] = mapped_column(ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False, index=True)

    box: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_bookmarked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    review_later: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_reviewed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_review_at: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

    user: Mapped["User"] = relationship(back_populates="flashcards")
    flashcard: Mapped["Flashcard"] = relationship(back_populates="user_states")
