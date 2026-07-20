import uuid
from datetime import date, datetime

from pydantic import BaseModel


class DailyStudyPoint(BaseModel):
    date: date
    minutes: int
    topics_completed: int


class RevisionItem(BaseModel):
    topic_id: uuid.UUID
    topic_name: str
    subject_name: str
    due_date: date
    interval_day: int
    overdue: bool


class SubjectCompletion(BaseModel):
    subject_id: uuid.UUID
    name: str
    slug: str
    completed: int
    total: int
    percent: float
    weightage_max_percent: float | None
    is_official_section: bool


class WeakStrongTopic(BaseModel):
    topic_id: uuid.UUID
    topic_name: str
    subject_name: str
    accuracy_percent: float


class LastSession(BaseModel):
    topic_name: str | None
    subject_name: str | None
    session_type: str
    started_at: datetime
    duration_minutes: int


class TodayTask(BaseModel):
    topic_id: uuid.UUID
    topic_name: str
    subject_name: str
    kind: str  # 'revision' | 'in_progress'


class DashboardSummary(BaseModel):
    greeting_name: str
    exam_date: date | None
    days_remaining: int | None
    target_score: int | None
    target_air: int | None

    current_streak_days: int
    longest_streak_days: int
    last_active_date: date | None

    topics_total: int
    topics_completed: int
    topics_in_progress: int
    topics_not_started: int
    topics_needs_revision: int
    weightage_completed_percent: float
    remaining_hours: float
    predicted_completion_date: date | None

    difficulty_distribution: dict[str, int]
    subject_completion: list[SubjectCompletion]

    study_minutes_today: int
    study_minutes_week: int
    study_minutes_month: int
    weekly_series: list[DailyStudyPoint]
    last_session: LastSession | None

    revision_due_today: int
    upcoming_revisions: list[RevisionItem]
    today_tasks: list[TodayTask]

    weak_topics: list[WeakStrongTopic]
    strong_topics: list[WeakStrongTopic]

    # Honest nulls until the Mock/Practice engines produce data (frontend shows onboarding).
    predicted_marks: float | None
    predicted_air: int | None
    next_mock_date: date | None
    has_accuracy_data: bool
    has_mock_data: bool
