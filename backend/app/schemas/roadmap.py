from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import Difficulty, NodeLevel, PriorityLevel, ProgressStatus


class TopicProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: ProgressStatus
    completion_percent: float
    retention_percent: float | None
    accuracy_percent: float | None
    pyqs_solved: int
    practice_solved: int
    revision_count: int
    time_spent_minutes: int
    last_studied_at: datetime | None
    last_revised_at: datetime | None
    completed_at: datetime | None


DEFAULT_PROGRESS = TopicProgressRead(
    status=ProgressStatus.NOT_STARTED,
    completion_percent=0.0,
    retention_percent=None,
    accuracy_percent=None,
    pyqs_solved=0,
    practice_solved=0,
    revision_count=0,
    time_spent_minutes=0,
    last_studied_at=None,
    last_revised_at=None,
    completed_at=None,
)


class TopicNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    level: NodeLevel
    order_index: int
    difficulty: Difficulty | None
    importance_1to5: int | None
    pyq_frequency: str | None
    estimated_hours: float | None
    revision_frequency: str | None
    prerequisites_text: str | None
    progress: TopicProgressRead
    children: list["TopicNode"] = []


class SubjectProgressSummary(BaseModel):
    total: int
    completed: int
    in_progress: int
    not_started: int
    needs_revision: int
    avg_completion_percent: float


class SubjectNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: str | None
    weightage_min_percent: float | None
    weightage_max_percent: float | None
    difficulty: Difficulty | None
    priority: PriorityLevel | None
    order_index: int
    is_official_section: bool
    progress_summary: SubjectProgressSummary
    topics: list[TopicNode]


class ProgressUpdateRequest(BaseModel):
    status: ProgressStatus | None = None
    completion_percent: float | None = None
    time_spent_minutes_delta: int | None = None
