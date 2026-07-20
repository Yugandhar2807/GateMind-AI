import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.enums import SessionType
from app.models.progress import StudySession
from app.models.user import User


def update_streak(user: User, day: date) -> None:
    """Advance the user's streak for a day of activity (idempotent within the same day)."""
    if user.last_active_date == day:
        return
    if user.last_active_date == day - timedelta(days=1):
        user.current_streak_days += 1
    else:
        user.current_streak_days = 1
    user.longest_streak_days = max(user.longest_streak_days, user.current_streak_days)
    user.last_active_date = day


def record_activity(
    db: Session, user: User, *, minutes: int, session_type: SessionType, topic_id: uuid.UUID | None
) -> None:
    """
    Log an instantaneous study session and update the streak — used by features (roadmap,
    flashcards, practice) that mark activity without an explicit start/stop timer. Explicit
    focus sessions use StudyService instead.
    """
    now = datetime.now(timezone.utc)
    db.add(
        StudySession(
            user_id=user.id,
            topic_id=topic_id,
            session_type=session_type,
            started_at=now,
            ended_at=now,
            duration_minutes=max(minutes, 0),
        )
    )
    update_streak(user, now.date())
