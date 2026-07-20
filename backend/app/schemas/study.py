import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import SessionType


class StudySessionStart(BaseModel):
    topic_id: uuid.UUID | None = None
    session_type: SessionType = SessionType.LEARNING


class StudySessionStop(BaseModel):
    notes: str | None = None
    interruptions: int = Field(default=0, ge=0)
    focus_score: int | None = Field(default=None, ge=0, le=100)


class StudySessionRead(BaseModel):
    id: uuid.UUID
    topic_id: uuid.UUID | None
    topic_name: str | None
    subject_name: str | None
    session_type: SessionType
    started_at: datetime
    ended_at: datetime | None
    duration_minutes: int
    interruptions: int
    focus_score: int | None
    notes: str | None
    is_active: bool
