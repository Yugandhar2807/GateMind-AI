from datetime import datetime

from pydantic import BaseModel

from app.models.enums import BookmarkType


class BookmarkToggleRequest(BaseModel):
    bookmark_type: BookmarkType
    target_id: int
    notes: str | None = None


class BookmarkToggleResponse(BaseModel):
    bookmarked: bool
    bookmark_id: int | None


class BookmarkRead(BaseModel):
    id: int
    bookmark_type: BookmarkType
    target_id: int
    notes: str | None
    created_at: datetime

    # Resolved at read time from the target's own table — never duplicated/stale data.
    title: str
    subtitle: str | None
    link: str
    is_missing: bool = False
