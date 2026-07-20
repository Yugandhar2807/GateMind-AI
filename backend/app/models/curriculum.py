from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, enum_col
from app.models.enums import (
    Difficulty,
    NodeLevel,
    PriorityLevel,
    ResourceCategory,
    ResourceLevel,
    ResourceRank,
    ResourceType,
)

# ---- Global curriculum (shared by all users; sourced from GATE-DA-2027) ----


class Subject(Base):
    __tablename__ = "subjects"

    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    weightage_min_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    weightage_max_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    difficulty: Mapped[Difficulty | None] = mapped_column(enum_col(Difficulty), nullable=True)
    priority: Mapped[PriorityLevel | None] = mapped_column(enum_col(PriorityLevel), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_official_section: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    color: Mapped[str | None] = mapped_column(String(32), nullable=True)


class Topic(Base):
    __tablename__ = "topics"

    subject_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # Self-referential tree for subtopics/concepts.
    parent_topic_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), index=True, nullable=True
    )
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[NodeLevel] = mapped_column(enum_col(NodeLevel), default=NodeLevel.TOPIC, nullable=False)
    difficulty: Mapped[Difficulty | None] = mapped_column(enum_col(Difficulty), nullable=True)
    importance_1to5: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pyq_frequency: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    revision_frequency: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prerequisites_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Rich learning content (Markdown; honestly empty until written)
    introduction: Mapped[str | None] = mapped_column(Text, nullable=True)
    theory_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    formulas_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    real_world_applications_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    cheat_sheet_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    common_mistakes_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    mind_map_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class TopicPrerequisite(Base):
    """Directed edge of the knowledge dependency graph: `topic` requires `prerequisite`."""

    __tablename__ = "topic_prerequisites"
    __table_args__ = (
        UniqueConstraint("topic_id", "prerequisite_topic_id"),
    )

    topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    prerequisite_topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    strength: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class Resource(Base):
    __tablename__ = "resources"

    type: Mapped[ResourceType] = mapped_column(enum_col(ResourceType), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    level: Mapped[ResourceLevel | None] = mapped_column(enum_col(ResourceLevel), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_free: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ---- Rich curation metadata ----
    category: Mapped[ResourceCategory | None] = mapped_column(enum_col(ResourceCategory), nullable=True)
    ranking: Mapped[ResourceRank | None] = mapped_column(enum_col(ResourceRank), nullable=True)
    instructor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    channel: Mapped[str | None] = mapped_column(String(255), nullable=True)
    organization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(64), default="English", nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    why_recommended: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_verified: Mapped[date | None] = mapped_column(Date, nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_obsolete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class TopicResource(Base):
    """Junction: which resources belong to a topic, and how prominently (curated first)."""

    __tablename__ = "topic_resources"
    __table_args__ = (
        UniqueConstraint("topic_id", "resource_id"),
    )

    topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), index=True, nullable=False
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"), index=True, nullable=False
    )
    relevance_rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_topic_specific: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
