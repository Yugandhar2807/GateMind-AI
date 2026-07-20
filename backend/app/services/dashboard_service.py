from collections import defaultdict
from datetime import datetime, timedelta, timezone
from math import ceil

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.curriculum import Subject, Topic
from app.models.enums import Difficulty, ProgressStatus, RevisionStatus
from app.models.progress import RevisionSchedule, StudySession, UserTopicProgress
from app.models.user import User
from app.schemas.dashboard import (
    DailyStudyPoint,
    DashboardSummary,
    LastSession,
    RevisionItem,
    SubjectCompletion,
    TodayTask,
    WeakStrongTopic,
)

WEEK_DAYS = 7
UPCOMING_LIMIT = 8
TODAY_TASK_LIMIT = 6
WEAK_STRONG_LIMIT = 5


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self, user: User) -> DashboardSummary:
        today = datetime.now(timezone.utc).date()
        # Fall back to the global GATE exam date so the hero countdown is useful before the
        # user sets a personal date.
        exam_date = user.exam_date or settings.GATE_EXAM_DATE
        days_remaining = (exam_date - today).days if exam_date else None

        subjects = {s.id: s for s in self.db.scalars(select(Subject)).all()}
        topics = list(self.db.scalars(select(Topic)).all())
        topic_by_id = {t.id: t for t in topics}
        progress_rows = list(
            self.db.scalars(select(UserTopicProgress).where(UserTopicProgress.user_id == user.id)).all()
        )
        progress_by_topic = {p.topic_id: p for p in progress_rows}

        status_counts = {s: 0 for s in ProgressStatus}
        total_importance = completed_importance = 0
        remaining_hours = 0.0
        difficulty_distribution = {d.value: 0 for d in Difficulty}
        subj_completed: dict = defaultdict(int)
        subj_total: dict = defaultdict(int)

        for t in topics:
            weight = t.importance_1to5 or 1
            total_importance += weight
            p = progress_by_topic.get(t.id)
            status = p.status if p else ProgressStatus.NOT_STARTED
            status_counts[status] += 1
            subj_total[t.subject_id] += 1
            if t.difficulty is not None:
                difficulty_distribution[t.difficulty.value] += 1
            if status == ProgressStatus.COMPLETED:
                completed_importance += weight
                subj_completed[t.subject_id] += 1
            else:
                remaining_hours += t.estimated_hours or 0.0

        weightage_completed_percent = (
            round(100 * completed_importance / total_importance, 1) if total_importance else 0.0
        )
        completed_count = status_counts[ProgressStatus.COMPLETED]

        subject_completion = []
        for s in sorted(subjects.values(), key=lambda x: x.order_index):
            total = subj_total.get(s.id, 0)
            done = subj_completed.get(s.id, 0)
            subject_completion.append(
                SubjectCompletion(
                    subject_id=s.id,
                    name=s.name,
                    slug=s.slug,
                    completed=done,
                    total=total,
                    percent=round(100 * done / total, 1) if total else 0.0,
                    weightage_max_percent=s.weightage_max_percent,
                    is_official_section=s.is_official_section,
                )
            )

        # Predicted completion date from the actual completion pace (needs a little signal).
        predicted_completion_date = None
        completed_dates = [p.completed_at.date() for p in progress_rows if p.completed_at]
        if completed_count >= 3 and completed_dates:
            days_active = max(1, (today - min(completed_dates)).days + 1)
            rate = completed_count / days_active
            remaining_topics = len(topics) - completed_count
            if rate > 0 and remaining_topics > 0:
                predicted_completion_date = today + timedelta(days=ceil(remaining_topics / rate))

        # Study minutes (today / week / month) + weekly series.
        week_start = today - timedelta(days=WEEK_DAYS - 1)
        month_start = today.replace(day=1)
        floor = min(week_start, month_start)
        sessions = list(
            self.db.scalars(
                select(StudySession).where(
                    StudySession.user_id == user.id,
                    StudySession.started_at >= datetime.combine(floor, datetime.min.time(), tzinfo=timezone.utc),
                )
            ).all()
        )
        minutes_by_day: dict = defaultdict(int)
        minutes_today = minutes_week = minutes_month = 0
        for s in sessions:
            d = s.started_at.date()
            if d >= week_start:
                minutes_by_day[d] += s.duration_minutes
                minutes_week += s.duration_minutes
            if d == today:
                minutes_today += s.duration_minutes
            if d >= month_start:
                minutes_month += s.duration_minutes

        completions_by_day: dict = defaultdict(int)
        for p in progress_rows:
            if p.completed_at and p.completed_at.date() >= week_start:
                completions_by_day[p.completed_at.date()] += 1
        weekly_series = [
            DailyStudyPoint(
                date=week_start + timedelta(days=i),
                minutes=minutes_by_day.get(week_start + timedelta(days=i), 0),
                topics_completed=completions_by_day.get(week_start + timedelta(days=i), 0),
            )
            for i in range(WEEK_DAYS)
        ]

        last = self.db.scalars(
            select(StudySession)
            .where(StudySession.user_id == user.id, StudySession.ended_at.isnot(None))
            .order_by(StudySession.started_at.desc())
        ).first()
        last_session = None
        if last is not None:
            lt = topic_by_id.get(last.topic_id) if last.topic_id else None
            ls = subjects.get(lt.subject_id) if lt else None
            last_session = LastSession(
                topic_name=lt.name if lt else None,
                subject_name=ls.name if ls else None,
                session_type=last.session_type.value,
                started_at=last.started_at,
                duration_minutes=last.duration_minutes,
            )

        # Revisions.
        rev_rows = list(
            self.db.scalars(
                select(RevisionSchedule)
                .where(RevisionSchedule.user_id == user.id, RevisionSchedule.status == RevisionStatus.PENDING)
                .order_by(RevisionSchedule.due_date)
            ).all()
        )
        revision_due_today = sum(1 for r in rev_rows if r.due_date <= today)
        upcoming_revisions = []
        for r in rev_rows[:UPCOMING_LIMIT]:
            t = topic_by_id.get(r.topic_id)
            subj = subjects.get(t.subject_id) if t else None
            if t and subj:
                upcoming_revisions.append(
                    RevisionItem(
                        topic_id=t.id,
                        topic_name=t.name,
                        subject_name=subj.name,
                        due_date=r.due_date,
                        interval_day=r.interval_day,
                        overdue=r.due_date < today,
                    )
                )

        # Today's tasks: due-today revisions first, then in-progress topics.
        today_tasks: list[TodayTask] = []
        for r in rev_rows:
            if r.due_date <= today and len(today_tasks) < TODAY_TASK_LIMIT:
                t = topic_by_id.get(r.topic_id)
                subj = subjects.get(t.subject_id) if t else None
                if t and subj:
                    today_tasks.append(
                        TodayTask(topic_id=t.id, topic_name=t.name, subject_name=subj.name, kind="revision")
                    )
        for p in progress_rows:
            if p.status == ProgressStatus.IN_PROGRESS and len(today_tasks) < TODAY_TASK_LIMIT:
                t = topic_by_id.get(p.topic_id)
                subj = subjects.get(t.subject_id) if t else None
                if t and subj:
                    today_tasks.append(
                        TodayTask(topic_id=t.id, topic_name=t.name, subject_name=subj.name, kind="in_progress")
                    )

        # Weak / strong topics (only once accuracy exists).
        acc_rows = [p for p in progress_rows if p.accuracy_percent is not None]

        def _ws(p) -> WeakStrongTopic:
            t = topic_by_id[p.topic_id]
            subj = subjects[t.subject_id]
            return WeakStrongTopic(
                topic_id=t.id, topic_name=t.name, subject_name=subj.name, accuracy_percent=p.accuracy_percent
            )

        weak_topics = [_ws(p) for p in sorted(acc_rows, key=lambda p: p.accuracy_percent)[:WEAK_STRONG_LIMIT]]
        strong_topics = [_ws(p) for p in sorted(acc_rows, key=lambda p: -p.accuracy_percent)[:WEAK_STRONG_LIMIT]]

        name_parts = (user.full_name or "").split()
        return DashboardSummary(
            greeting_name=name_parts[0] if name_parts else "there",
            exam_date=exam_date,
            days_remaining=days_remaining,
            target_score=user.target_score,
            target_air=user.target_air,
            current_streak_days=user.current_streak_days,
            longest_streak_days=user.longest_streak_days,
            last_active_date=user.last_active_date,
            topics_total=len(topics),
            topics_completed=completed_count,
            topics_in_progress=status_counts[ProgressStatus.IN_PROGRESS],
            topics_not_started=status_counts[ProgressStatus.NOT_STARTED],
            topics_needs_revision=status_counts[ProgressStatus.NEEDS_REVISION],
            weightage_completed_percent=weightage_completed_percent,
            remaining_hours=round(remaining_hours, 1),
            predicted_completion_date=predicted_completion_date,
            difficulty_distribution=difficulty_distribution,
            subject_completion=subject_completion,
            study_minutes_today=minutes_today,
            study_minutes_week=minutes_week,
            study_minutes_month=minutes_month,
            weekly_series=weekly_series,
            last_session=last_session,
            revision_due_today=revision_due_today,
            upcoming_revisions=upcoming_revisions,
            today_tasks=today_tasks,
            weak_topics=weak_topics,
            strong_topics=strong_topics,
            predicted_marks=None,
            predicted_air=None,
            next_mock_date=None,
            has_accuracy_data=len(acc_rows) > 0,
            has_mock_data=False,
        )
