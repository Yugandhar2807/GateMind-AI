from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import Difficulty


class FlashcardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int
    topic_name: str
    subject_name: str
    front_markdown: str
    back_markdown: str
    difficulty: Difficulty
    box: int
    is_bookmarked: bool
    is_favorite: bool
    review_later: bool
    next_review_at: date | None


class ReviewRequest(BaseModel):
    correct: bool


class FlashcardStateUpdate(BaseModel):
    is_bookmarked: bool | None = None
    is_favorite: bool | None = None
    review_later: bool | None = None
