import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.study import StudySessionRead, StudySessionStart, StudySessionStop
from app.services.study_service import SessionNotFoundError, StudyService

router = APIRouter(prefix="/study", tags=["study"])


@router.post("/sessions/start", response_model=StudySessionRead, status_code=status.HTTP_201_CREATED)
def start_session(
    payload: StudySessionStart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudySessionRead:
    return StudyService(db).start(current_user, payload)


@router.post("/sessions/{session_id}/stop", response_model=StudySessionRead)
def stop_session(
    session_id: uuid.UUID,
    payload: StudySessionStop,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudySessionRead:
    try:
        return StudyService(db).stop(current_user, session_id, payload)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study session not found") from exc


@router.get("/sessions/active", response_model=StudySessionRead | None)
def active_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudySessionRead | None:
    return StudyService(db).active(current_user)


@router.get("/sessions", response_model=list[StudySessionRead])
def recent_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[StudySessionRead]:
    return StudyService(db).recent(current_user)
