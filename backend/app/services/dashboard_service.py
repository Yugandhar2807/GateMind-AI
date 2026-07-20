from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.content import Subject, Topic
from app.models.enums import ProgressStatus, RevisionStatus
from app.models.progress import StudySession, UserTopicProgress
from app.models.revision import RevisionSchedule
from app.models.user import User
from app.schemas.dashboard import DailyStudyPoint, DashboardSummary, UpcomingRevision, WeakStrongTopic

UPCOMING_REVISIONS_LIMIT = 5
WEEK_SERIES_DAYS = 7


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self, user: User) -> DashboardSummary:
        today = datetime.utcnow().date()

        days_remaining = (user.exam_date - today).days if user.exam_date else None

        topics = self.db.scalars(select(Topic)).all()
        progress_rows = self.db.scalars(
            select(UserTopicProgress).where(UserTopicProgress.user_id == user.id)
        ).all()
        progress_by_topic = {p.topic_id: p for p in progress_rows}

        status_counts = {s: 0 for s in ProgressStatus}
        total_importance = 0
        completed_importance = 0
        for topic in topics:
            weight = topic.importance_1to5 or 1
            total_importance += weight
            progress = progress_by_topic.get(topic.id)
            status = progress.status if progress else ProgressStatus.NOT_STARTED
            status_counts[status] += 1
            if status == ProgressStatus.COMPLETED:
                completed_importance += weight

        weightage_completed_percent = (
            round(100 * completed_importance / total_importance, 1) if total_importance else None
        )

        week_start = today - timedelta(days=WEEK_SERIES_DAYS - 1)
        sessions = self.db.scalars(
            select(StudySession).where(
                StudySession.user_id == user.id,
                StudySession.started_at >= datetime.combine(week_start, datetime.min.time()),
            )
        ).all()

        minutes_by_day: dict[date, int] = defaultdict(int)
        month_start = today.replace(day=1)
        minutes_today = 0
        minutes_week = 0
        minutes_month = 0
        for s in sessions:
            d = s.started_at.date()
            minutes_by_day[d] += s.duration_minutes
            if d == today:
                minutes_today += s.duration_minutes
            if d >= week_start:
                minutes_week += s.duration_minutes
            if d >= month_start:
                minutes_month += s.duration_minutes

        completions_by_day: dict[date, int] = defaultdict(int)
        for p in progress_rows:
            if p.completed_at and p.completed_at.date() >= week_start:
                completions_by_day[p.completed_at.date()] += 1

        weekly_series = [
            DailyStudyPoint(
                date=week_start + timedelta(days=i),
                minutes=minutes_by_day.get(week_start + timedelta(days=i), 0),
                topics_completed=completions_by_day.get(week_start + timedelta(days=i), 0),
            )
            for i in range(WEEK_SERIES_DAYS)
        ]

        revision_rows = self.db.execute(
            select(RevisionSchedule, Topic, Subject)
            .join(Topic, RevisionSchedule.topic_id == Topic.id)
            .join(Subject, Topic.subject_id == Subject.id)
            .where(
                RevisionSchedule.user_id == user.id,
                RevisionSchedule.status == RevisionStatus.PENDING,
                RevisionSchedule.scheduled_date >= today,
            )
            .order_by(RevisionSchedule.scheduled_date)
            .limit(UPCOMING_REVISIONS_LIMIT)
        ).all()

        upcoming_revisions = [
            UpcomingRevision(
                topic_id=topic.id,
                topic_name=topic.name,
                subject_name=subject.name,
                scheduled_date=schedule.scheduled_date,
                interval_stage=schedule.interval_stage.value,
            )
            for schedule, topic, subject in revision_rows
        ]

        weak_rows = self.db.execute(
            select(UserTopicProgress, Topic, Subject)
            .join(Topic, UserTopicProgress.topic_id == Topic.id)
            .join(Subject, Topic.subject_id == Subject.id)
            .where(UserTopicProgress.user_id == user.id, UserTopicProgress.accuracy_percent.isnot(None))
            .order_by(UserTopicProgress.accuracy_percent.asc())
            .limit(UPCOMING_REVISIONS_LIMIT)
        ).all()
        weak_topics = [
            WeakStrongTopic(
                topic_id=t.id, topic_name=t.name, subject_name=s.name, accuracy_percent=p.accuracy_percent
            )
            for p, t, s in weak_rows
        ]
        strong_rows = self.db.execute(
            select(UserTopicProgress, Topic, Subject)
            .join(Topic, UserTopicProgress.topic_id == Topic.id)
            .join(Subject, Topic.subject_id == Subject.id)
            .where(UserTopicProgress.user_id == user.id, UserTopicProgress.accuracy_percent.isnot(None))
            .order_by(UserTopicProgress.accuracy_percent.desc())
            .limit(UPCOMING_REVISIONS_LIMIT)
        ).all()
        strong_topics = [
            WeakStrongTopic(
                topic_id=t.id, topic_name=t.name, subject_name=s.name, accuracy_percent=p.accuracy_percent
            )
            for p, t, s in strong_rows
        ]

        return DashboardSummary(
            exam_date=user.exam_date,
            days_remaining=days_remaining,
            target_score=user.target_score,
            target_air=user.target_air,
            current_streak_days=user.current_streak_days,
            longest_streak_days=user.longest_streak_days,
            topics_total=len(topics),
            topics_completed=status_counts[ProgressStatus.COMPLETED],
            topics_in_progress=status_counts[ProgressStatus.IN_PROGRESS],
            topics_not_started=status_counts[ProgressStatus.NOT_STARTED],
            topics_needs_revision=status_counts[ProgressStatus.NEEDS_REVISION],
            weightage_completed_percent=weightage_completed_percent,
            study_minutes_today=minutes_today,
            study_minutes_week=minutes_week,
            study_minutes_month=minutes_month,
            weekly_series=weekly_series,
            upcoming_revisions=upcoming_revisions,
            weak_topics=weak_topics,
            strong_topics=strong_topics,
            # Practice/mock/prediction engines don't exist yet (Phases 5-7) — honestly null
            # rather than fabricated, per the project's no-fake-implementation requirement.
            predicted_marks=None,
            predicted_air=None,
            next_mock_date=None,
        )
