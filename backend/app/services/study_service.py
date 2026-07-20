import uuid
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.curriculum import Subject, Topic
from app.models.progress import StudySession
from app.models.user import User
from app.schemas.study import StudySessionRead, StudySessionStart, StudySessionStop
from app.services.activity_service import update_streak

RECENT_LIMIT = 10


class SessionNotFoundError(Exception):
    pass


class StudyService:
    def __init__(self, db: Session):
        self.db = db

    def _names(self, topic_id: uuid.UUID | None) -> tuple[str | None, str | None]:
        if topic_id is None:
            return None, None
        row = self.db.execute(
            select(Topic.name, Subject.name)
            .join(Subject, Topic.subject_id == Subject.id)
            .where(Topic.id == topic_id)
        ).first()
        return (row[0], row[1]) if row else (None, None)

    def _read(self, s: StudySession) -> StudySessionRead:
        topic_name, subject_name = self._names(s.topic_id)
        return StudySessionRead(
            id=s.id,
            topic_id=s.topic_id,
            topic_name=topic_name,
            subject_name=subject_name,
            session_type=s.session_type,
            started_at=s.started_at,
            ended_at=s.ended_at,
            duration_minutes=s.duration_minutes,
            interruptions=s.interruptions,
            focus_score=s.focus_score,
            notes=s.notes,
            is_active=s.ended_at is None,
        )

    def _active_row(self, user_id: uuid.UUID) -> StudySession | None:
        return self.db.scalars(
            select(StudySession)
            .where(StudySession.user_id == user_id, StudySession.ended_at.is_(None))
            .order_by(desc(StudySession.started_at))
        ).first()

    def start(self, user: User, payload: StudySessionStart) -> StudySessionRead:
        # One active session at a time — return the existing one instead of stacking.
        active = self._active_row(user.id)
        if active is not None:
            return self._read(active)
        s = StudySession(
            user_id=user.id,
            topic_id=payload.topic_id,
            session_type=payload.session_type,
            started_at=datetime.now(timezone.utc),
            duration_minutes=0,
        )
        self.db.add(s)
        self.db.commit()
        self.db.refresh(s)
        return self._read(s)

    def stop(self, user: User, session_id: uuid.UUID, payload: StudySessionStop) -> StudySessionRead:
        s = self.db.get(StudySession, session_id)
        if s is None or s.user_id != user.id:
            raise SessionNotFoundError(session_id)
        now = datetime.now(timezone.utc)
        if s.ended_at is None:
            s.ended_at = now
            s.duration_minutes = max(0, int((now - s.started_at).total_seconds() // 60))
            update_streak(user, now.date())
        s.notes = payload.notes
        s.interruptions = payload.interruptions
        s.focus_score = payload.focus_score
        self.db.commit()
        self.db.refresh(s)
        return self._read(s)

    def active(self, user: User) -> StudySessionRead | None:
        s = self._active_row(user.id)
        return self._read(s) if s else None

    def recent(self, user: User, limit: int = RECENT_LIMIT) -> list[StudySessionRead]:
        rows = self.db.scalars(
            select(StudySession)
            .where(StudySession.user_id == user.id, StudySession.ended_at.isnot(None))
            .order_by(desc(StudySession.started_at))
            .limit(limit)
        ).all()
        return [self._read(s) for s in rows]
