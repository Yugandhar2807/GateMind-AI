import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content_markdown: str = ""
    topic_id: uuid.UUID | None = None


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content_markdown: str | None = None
    topic_id: uuid.UUID | None = None


class NoteRead(BaseModel):
    id: uuid.UUID
    title: str
    content_markdown: str
    topic_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
