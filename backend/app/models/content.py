from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import Difficulty, NodeLevel, PriorityLevel, ResourceLevel, ResourceType

if TYPE_CHECKING:
    from app.models.progress import UserTopicProgress
    from app.models.question import Question
    from app.models.flashcard import Flashcard
    from app.models.mock import MockTestQuestion


class Subject(Base):
    """Top level of the roadmap: the 7 official GATE DA sections + General Aptitude."""

    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    weightage_min_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    weightage_max_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    difficulty: Mapped[Difficulty | None] = mapped_column(Enum(Difficulty), nullable=True)
    priority: Mapped[PriorityLevel | None] = mapped_column(Enum(PriorityLevel), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    color_hex: Mapped[str | None] = mapped_column(String(16), nullable=True)
    # False for "Deep Learning (MLP sub-topic)" and "Data Science & Big Data Tools" — both are
    # tracked separately for study convenience but are NOT official standalone GATE DA sections.
    is_official_section: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    topics: Mapped[list["Topic"]] = relationship(back_populates="subject", cascade="all, delete-orphan")


class Topic(Base):
    """
    Self-referential tree under a Subject: Topic -> Subtopic -> Concept.
    `level` labels depth for UI grouping; `parent_id` null means a top-level Topic.
    """

    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=True, index=True)

    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[NodeLevel] = mapped_column(Enum(NodeLevel), default=NodeLevel.TOPIC, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    difficulty: Mapped[Difficulty | None] = mapped_column(Enum(Difficulty), nullable=True)
    importance_1to5: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_weightage_marks: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Free-form prose from research ("Zero — confirmed absent from the official syllabus..."),
    # not a short label — observed up to ~490 chars, so Text rather than a bounded VARCHAR.
    pyq_frequency: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    revision_frequency: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Rich content (Phase 3 populates these in full; nullable until then, never fake-filled)
    introduction: Mapped[str | None] = mapped_column(Text, nullable=True)
    theory_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    formulas_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    real_world_applications: Mapped[str | None] = mapped_column(Text, nullable=True)
    mind_map_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    cheat_sheet_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    common_mistakes_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)

    prerequisites_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # human-readable prereq names, seeded from research

    subject: Mapped["Subject"] = relationship(back_populates="topics")
    parent: Mapped["Topic | None"] = relationship(remote_side="Topic.id", back_populates="children")
    children: Mapped[list["Topic"]] = relationship(back_populates="parent", cascade="all, delete-orphan")

    resource_links: Mapped[list["TopicResource"]] = relationship(back_populates="topic", cascade="all, delete-orphan")
    progress_entries: Mapped[list["UserTopicProgress"]] = relationship(back_populates="topic", cascade="all, delete-orphan")
    questions: Mapped[list["Question"]] = relationship(back_populates="topic", cascade="all, delete-orphan")
    flashcards: Mapped[list["Flashcard"]] = relationship(back_populates="topic", cascade="all, delete-orphan")
    mock_questions: Mapped[list["MockTestQuestion"]] = relationship(back_populates="topic")


class Resource(Base):
    """A learning resource: video, course-adjacent link, book, blog, paper, repo, etc."""

    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    resource_type: Mapped[ResourceType] = mapped_column(Enum(ResourceType), nullable=False)
    level: Mapped[ResourceLevel] = mapped_column(Enum(ResourceLevel), default=ResourceLevel.BEGINNER, nullable=False)

    # Nullable deliberately: some curated resources (e.g. a recommended textbook cited by
    # title only) have no single canonical URL in the source research. We never fabricate
    # a link that wasn't actually verified — see scripts/seed.py for the extraction rule.
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    platform: Mapped[str | None] = mapped_column(String(120), nullable=True)  # YouTube, NPTEL, MIT OCW, ...
    instructor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str] = mapped_column(String(64), default="English", nullable=False)
    is_free: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)  # curator-assessed 0-5, editable via admin panel

    topic_links: Mapped[list["TopicResource"]] = relationship(back_populates="resource", cascade="all, delete-orphan")


class TopicResource(Base):
    """Many-to-many join: a resource can serve multiple topics, ranked per topic."""

    __tablename__ = "topic_resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    relevance_rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0 = best fit

    topic: Mapped["Topic"] = relationship(back_populates="resource_links")
    resource: Mapped["Resource"] = relationship(back_populates="topic_links")
