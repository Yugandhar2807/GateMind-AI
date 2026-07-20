from datetime import date

from pydantic import BaseModel


class DailyStudyPoint(BaseModel):
    date: date
    minutes: int
    topics_completed: int


class UpcomingRevision(BaseModel):
    topic_id: int
    topic_name: str
    subject_name: str
    scheduled_date: date
    interval_stage: int


class WeakStrongTopic(BaseModel):
    topic_id: int
    topic_name: str
    subject_name: str
    accuracy_percent: float


class DashboardSummary(BaseModel):
    exam_date: date | None
    days_remaining: int | None

    target_score: int | None
    target_air: int | None

    current_streak_days: int
    longest_streak_days: int

    topics_total: int
    topics_completed: int
    topics_in_progress: int
    topics_not_started: int
    topics_needs_revision: int
    weightage_completed_percent: float | None

    study_minutes_today: int
    study_minutes_week: int
    study_minutes_month: int
    weekly_series: list[DailyStudyPoint]

    upcoming_revisions: list[UpcomingRevision]

    weak_topics: list[WeakStrongTopic]
    strong_topics: list[WeakStrongTopic]

    predicted_marks: float | None
    predicted_air: int | None
    next_mock_date: date | None
