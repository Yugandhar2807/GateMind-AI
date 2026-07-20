from pydantic import BaseModel, ConfigDict

from app.models.enums import Difficulty, NodeLevel, ResourceLevel, ResourceType
from app.schemas.roadmap import TopicProgressRead


class ResourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    resource_type: ResourceType
    level: ResourceLevel
    url: str | None
    platform: str | None
    instructor: str | None
    description: str | None
    is_free: bool


class TopicDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    level: NodeLevel
    difficulty: Difficulty | None
    importance_1to5: int | None
    pyq_frequency: str | None
    estimated_hours: float | None
    revision_frequency: str | None
    prerequisites_text: str | None

    # Rich content — null/empty means "not written yet", shown honestly in the UI, never faked.
    introduction: str | None
    theory_markdown: str | None
    formulas_markdown: str | None
    real_world_applications: str | None
    mind_map_json: str | None
    cheat_sheet_markdown: str | None
    common_mistakes_markdown: str | None

    subject_id: int
    subject_name: str
    subject_slug: str

    progress: TopicProgressRead
    resources: list[ResourceRead]
