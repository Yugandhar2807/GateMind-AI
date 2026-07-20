from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import RevisionInterval, RevisionStatus

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.content import Topic


class RevisionSchedule(Base):
    """
    One row per spaced-repetition checkpoint for a (user, topic): the 1/3/7/15/30/60/90-day
    ladder. A new row is created for the next interval once the current one completes.
    """

    __tablename__ = "revision_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)

    interval_stage: Mapped[RevisionInterval] = mapped_column(Enum(RevisionInterval), nullable=False)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[RevisionStatus] = mapped_column(Enum(RevisionStatus), default=RevisionStatus.PENDING, nullable=False)
    retention_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    user: Mapped["User"] = relationship(back_populates="revision_schedules")
    topic: Mapped["Topic"] = relationship()
