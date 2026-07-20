import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import Difficulty


class FlashcardRead(BaseModel):
    id: uuid.UUID
    topic_id: uuid.UUID
    topic_name: str
    subject_name: str
    front_markdown: str
    back_markdown: str
    difficulty: Difficulty
    box: int
    is_bookmarked: bool
    is_favorite: bool
    review_later: bool
    next_review_at: datetime | None


class ReviewRequest(BaseModel):
    correct: bool


class FlashcardStateUpdate(BaseModel):
    is_bookmarked: bool | None = None
    is_favorite: bool | None = None
    review_later: bool | None = None
