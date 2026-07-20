import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ResourceCategory, ResourceLevel, ResourceRank, ResourceType


class ResourceAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: ResourceType
    title: str
    url: str | None
    description: str | None
    instructor: str | None
    channel: str | None
    organization: str | None
    provider: str | None
    level: ResourceLevel | None
    category: ResourceCategory | None
    ranking: ResourceRank | None
    duration_minutes: int | None
    year: int | None
    language: str
    rating: float | None
    why_recommended: str | None
    confidence_score: float | None
    last_verified: date | None
    needs_review: bool
    is_approved: bool
    is_obsolete: bool
    is_free: bool
    created_at: datetime


class ResourceCreate(BaseModel):
    type: ResourceType = ResourceType.ARTICLE
    title: str
    url: str | None = None
    description: str | None = None
    instructor: str | None = None
    channel: str | None = None
    organization: str | None = None
    level: ResourceLevel | None = None
    category: ResourceCategory | None = None
    ranking: ResourceRank | None = None
    duration_minutes: int | None = None
    year: int | None = None
    language: str = "English"
    rating: float | None = None
    why_recommended: str | None = None
    needs_review: bool = False
    topic_id: uuid.UUID | None = None  # optionally link to a topic on create


class ResourceUpdate(BaseModel):
    title: str | None = None
    url: str | None = None
    description: str | None = None
    instructor: str | None = None
    channel: str | None = None
    organization: str | None = None
    level: ResourceLevel | None = None
    category: ResourceCategory | None = None
    ranking: ResourceRank | None = None
    duration_minutes: int | None = None
    year: int | None = None
    language: str | None = None
    rating: float | None = None
    why_recommended: str | None = None
    needs_review: bool | None = None
    is_approved: bool | None = None
    is_obsolete: bool | None = None
