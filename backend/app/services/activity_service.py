import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.enums import SessionType
from app.models.progress import StudySession
from app.models.user import User


def record_activity(
    db: Session, user: User, *, minutes: int, session_type: SessionType, topic_id: uuid.UUID | None
) -> None:
    """
    Log a study session and update the user's streak — one source of truth for "the user did
    something today" so the dashboard's streak/study-time widgets stay correct regardless of which
    feature (roadmap, practice, mocks, flashcards) triggered the activity.
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

    today = now.date()
    if user.last_active_date == today:
        pass  # already counted today
    elif user.last_active_date == today - timedelta(days=1):
        user.current_streak_days += 1
    else:
        user.current_streak_days = 1
    user.longest_streak_days = max(user.longest_streak_days, user.current_streak_days)
    user.last_active_date = today
