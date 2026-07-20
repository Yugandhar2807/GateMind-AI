import uuid

from pydantic import BaseModel

from app.models.enums import Difficulty, QuestionSource, QuestionType


class PracticeStartRequest(BaseModel):
    topic_id: uuid.UUID | None = None
    subject_id: uuid.UUID | None = None
    difficulty: Difficulty | None = None
    question_count: int = 10


class QuestionPublic(BaseModel):
    """Question as shown DURING an attempt — never includes the answer."""

    id: uuid.UUID
    topic_id: uuid.UUID
    question_type: QuestionType
    difficulty: Difficulty
    source: QuestionSource
    source_year: int | None
    question_markdown: str
    options: list[str] | None
    marks: float
    negative_marks: float
    expected_time_seconds: int


class PracticeAttemptStarted(BaseModel):
    attempt_id: uuid.UUID
    topic_id: uuid.UUID | None
    questions: list[QuestionPublic]


class PracticeAnswerRequest(BaseModel):
    question_id: uuid.UUID
    selected_indices: list[int] | None = None
    nat_value: float | None = None
    is_skipped: bool = False
    time_taken_seconds: int


class PracticeAnswerResult(BaseModel):
    question_id: uuid.UUID
    is_correct: bool | None
    marks_awarded: float
    correct_option_indices: list[int]
    correct_value: float | None
    explanation_markdown: str | None


class PracticeSubmitResponse(BaseModel):
    attempt_id: uuid.UUID
    score: float
    max_score: float
    accuracy_percent: float
    correct_count: int
    incorrect_count: int
    skipped_count: int
    negative_marks_lost: float
    avg_time_per_question_seconds: float


class TopicQuestionStats(BaseModel):
    total: int
    by_difficulty: dict[str, int]
    by_type: dict[str, int]
