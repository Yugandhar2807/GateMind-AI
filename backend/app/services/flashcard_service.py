from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.enums import SessionType
from app.models.flashcard import Flashcard, UserFlashcard
from app.models.user import User
from app.repositories.flashcard_repository import FlashcardRepository
from app.schemas.flashcard import FlashcardRead, FlashcardStateUpdate
from app.services.activity_service import record_activity

BOX_INTERVAL_DAYS = {1: 1, 2: 3, 3: 7, 4: 15, 5: 30}
MAX_BOX = 5


class FlashcardNotFoundError(Exception):
    pass


class FlashcardService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FlashcardRepository(db)

    def _to_read(self, card: Flashcard, state: UserFlashcard | None) -> FlashcardRead:
        return FlashcardRead(
            id=card.id,
            topic_id=card.topic_id,
            topic_name=card.topic.name,
            subject_name=card.topic.subject.name,
            front_markdown=card.front_markdown,
            back_markdown=card.back_markdown,
            difficulty=card.difficulty,
            box=state.box if state else 1,
            is_bookmarked=state.is_bookmarked if state else False,
            is_favorite=state.is_favorite if state else False,
            review_later=state.review_later if state else False,
            next_review_at=state.next_review_at if state else None,
        )

    def list_all(self, user_id: int, *, topic_id: int | None = None) -> list[FlashcardRead]:
        cards = self.repo.list_all(topic_id=topic_id)
        states = self.repo.user_states_by_flashcard_id(user_id)
        return [self._to_read(c, states.get(c.id)) for c in cards]

    def due_today(self, user_id: int, *, today: date) -> list[FlashcardRead]:
        cards = self.repo.due_flashcards(user_id, today=today)
        states = self.repo.user_states_by_flashcard_id(user_id)
        return [self._to_read(c, states.get(c.id)) for c in cards]

    def review(self, user: User, flashcard_id: int, *, correct: bool, today: date) -> FlashcardRead:
        card = self.repo.get(flashcard_id)
        if card is None:
            raise FlashcardNotFoundError(flashcard_id)

        state = self.repo.get_or_create_state(user.id, flashcard_id)
        state.box = min(state.box + 1, MAX_BOX) if correct else 1
        state.next_review_at = today + timedelta(days=BOX_INTERVAL_DAYS[state.box])
        state.last_reviewed_at = today

        record_activity(self.db, user, minutes=0, session_type=SessionType.FLASHCARDS, topic_id=card.topic_id)

        self.db.commit()
        self.db.refresh(state)
        return self._to_read(card, state)

    def update_state(self, user_id: int, flashcard_id: int, payload: FlashcardStateUpdate) -> FlashcardRead:
        card = self.repo.get(flashcard_id)
        if card is None:
            raise FlashcardNotFoundError(flashcard_id)

        state = self.repo.get_or_create_state(user_id, flashcard_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(state, field, value)

        self.db.commit()
        self.db.refresh(state)
        return self._to_read(card, state)
