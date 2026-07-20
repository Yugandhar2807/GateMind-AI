from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import Difficulty, QuestionSource, QuestionType


class PracticeStartRequest(BaseModel):
    topic_id: int | None = None
    subject_id: int | None = None
    difficulty: Difficulty | None = None
    question_count: int = 10


class QuestionPublic(BaseModel):
    """Question as shown DURING an attempt — never includes the answer."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int
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
    attempt_id: int
    topic_id: int | None
    questions: list[QuestionPublic]


class PracticeAnswerRequest(BaseModel):
    question_id: int
    selected_indices: list[int] | None = None
    nat_value: float | None = None
    is_skipped: bool = False
    time_taken_seconds: int


class PracticeAnswerResult(BaseModel):
    question_id: int
    is_correct: bool | None
    marks_awarded: float
    correct_option_indices: list[int]
    correct_value: float | None
    explanation_markdown: str | None


class PracticeSubmitResponse(BaseModel):
    attempt_id: int
    score: float
    max_score: float
    accuracy_percent: float
    correct_count: int
    incorrect_count: int
    skipped_count: int
    negative_marks_lost: float
    avg_time_per_question_seconds: float


class PracticeAttemptSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int | None
    started_at: datetime
    submitted_at: datetime | None
    score: float | None
    accuracy_percent: float | None
    is_complete: bool


class TopicQuestionStats(BaseModel):
    total: int
    by_difficulty: dict[str, int]
    by_type: dict[str, int]
