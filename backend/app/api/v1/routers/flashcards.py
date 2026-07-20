from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.flashcard import FlashcardRead, FlashcardStateUpdate, ReviewRequest
from app.services.flashcard_service import FlashcardNotFoundError, FlashcardService

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


@router.get("", response_model=list[FlashcardRead])
def list_flashcards(
    topic_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FlashcardRead]:
    return FlashcardService(db).list_all(current_user.id, topic_id=topic_id)


@router.get("/due", response_model=list[FlashcardRead])
def due_flashcards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FlashcardRead]:
    return FlashcardService(db).due_today(current_user.id, today=datetime.utcnow().date())


@router.post("/{flashcard_id}/review", response_model=FlashcardRead)
def review_flashcard(
    flashcard_id: int,
    payload: ReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FlashcardRead:
    try:
        return FlashcardService(db).review(
            current_user, flashcard_id, correct=payload.correct, today=datetime.utcnow().date()
        )
    except FlashcardNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found") from exc


@router.patch("/{flashcard_id}/state", response_model=FlashcardRead)
def update_flashcard_state(
    flashcard_id: int,
    payload: FlashcardStateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FlashcardRead:
    try:
        return FlashcardService(db).update_state(current_user.id, flashcard_id, payload)
    except FlashcardNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found") from exc
