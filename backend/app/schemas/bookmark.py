import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import BookmarkType


class BookmarkToggleRequest(BaseModel):
    bookmark_type: BookmarkType
    target_id: uuid.UUID
    note: str | None = None


class BookmarkToggleResponse(BaseModel):
    bookmarked: bool
    bookmark_id: uuid.UUID | None


class BookmarkRead(BaseModel):
    id: uuid.UUID
    bookmark_type: BookmarkType
    target_id: uuid.UUID
    notes: str | None
    created_at: datetime

    # Resolved at read time from the target's own table — never duplicated/stale data.
    title: str
    subtitle: str | None
    link: str
    is_missing: bool = False
