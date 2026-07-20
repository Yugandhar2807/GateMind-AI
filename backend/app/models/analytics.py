from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User


class AnalyticsSnapshot(Base):
    """
    One row per (user, day): a denormalized daily rollup so trend charts (predicted AIR,
    accuracy, retention, study hours) don't require recomputation across raw tables on every
    dashboard load. Written by the nightly background scheduler.
    """

    __tablename__ = "analytics_snapshots"
    __table_args__ = (UniqueConstraint("user_id", "snapshot_date", name="uq_user_snapshot_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    study_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    topics_completed_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    accuracy_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    retention_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_marks: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_air: Mapped[int | None] = mapped_column(Integer, nullable=True)
    streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship(back_populates="analytics_snapshots")
