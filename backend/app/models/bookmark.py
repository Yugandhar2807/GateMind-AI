from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import BookmarkType

if TYPE_CHECKING:
    from app.models.user import User


class Bookmark(Base):
    """
    Polymorphic bookmark: (bookmark_type, target_id) points at a resource/question/topic/
    formula/note/flashcard row. Kept as a type+id pair rather than per-type tables so the
    bookshelf UI can query one table for "everything I've saved."
    """

    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("user_id", "bookmark_type", "target_id", name="uq_user_bookmark_target"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bookmark_type: Mapped[BookmarkType] = mapped_column(Enum(BookmarkType), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="bookmarks")
