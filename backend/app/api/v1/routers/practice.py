from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.practice_repository import PracticeRepository
from app.schemas.practice import (
    PracticeAnswerRequest,
    PracticeAnswerResult,
    PracticeAttemptStarted,
    PracticeAttemptSummary,
    PracticeStartRequest,
    PracticeSubmitResponse,
    TopicQuestionStats,
)
from app.services.practice_service import AttemptNotFoundError, PracticeService, QuestionNotInAttemptError

router = APIRouter(prefix="/practice", tags=["practice"])


@router.get("/topics/{topic_id}/stats", response_model=TopicQuestionStats)
def get_topic_stats(
    topic_id: int,
    db: Session = Depends(get_db),
) -> TopicQuestionStats:
    return PracticeService(db).topic_stats(topic_id)


@router.post("/start", response_model=PracticeAttemptStarted)
def start_practice(
    payload: PracticeStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PracticeAttemptStarted:
    return PracticeService(db).start(current_user.id, payload)


@router.post("/attempts/{attempt_id}/answer", response_model=PracticeAnswerResult)
def answer_question(
    attempt_id: int,
    payload: PracticeAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PracticeAnswerResult:
    try:
        return PracticeService(db).answer(current_user.id, attempt_id, payload)
    except AttemptNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found") from exc
    except QuestionNotInAttemptError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found") from exc


@router.post("/attempts/{attempt_id}/submit", response_model=PracticeSubmitResponse)
def submit_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PracticeSubmitResponse:
    try:
        return PracticeService(db).submit(current_user, attempt_id)
    except AttemptNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found") from exc


@router.get("/attempts", response_model=list[PracticeAttemptSummary])
def list_attempts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PracticeAttemptSummary]:
    return [
        PracticeAttemptSummary.model_validate(a) for a in PracticeRepository(db).list_attempts(current_user.id)
    ]
