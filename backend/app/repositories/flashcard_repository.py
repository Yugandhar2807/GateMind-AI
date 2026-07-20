from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.content import Topic
from app.models.flashcard import Flashcard, UserFlashcard


class FlashcardRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self, *, topic_id: int | None = None) -> list[Flashcard]:
        stmt = (
            select(Flashcard)
            .options(selectinload(Flashcard.topic).selectinload(Topic.subject))
            .order_by(Flashcard.id)
        )
        if topic_id is not None:
            stmt = stmt.where(Flashcard.topic_id == topic_id)
        return list(self.db.scalars(stmt).all())

    def get(self, flashcard_id: int) -> Flashcard | None:
        return self.db.get(Flashcard, flashcard_id)

    def user_states_by_flashcard_id(self, user_id: int) -> dict[int, UserFlashcard]:
        stmt = select(UserFlashcard).where(UserFlashcard.user_id == user_id)
        return {row.flashcard_id: row for row in self.db.scalars(stmt).all()}

    def get_or_create_state(self, user_id: int, flashcard_id: int) -> UserFlashcard:
        stmt = select(UserFlashcard).where(
            UserFlashcard.user_id == user_id, UserFlashcard.flashcard_id == flashcard_id
        )
        state = self.db.scalars(stmt).first()
        if state is None:
            state = UserFlashcard(user_id=user_id, flashcard_id=flashcard_id, box=1)
            self.db.add(state)
            self.db.flush()
        return state

    def due_flashcards(self, user_id: int, *, today: date, limit: int = 30) -> list[Flashcard]:
        states = self.user_states_by_flashcard_id(user_id)
        all_cards = self.list_all()
        due: list[Flashcard] = []
        for card in all_cards:
            state = states.get(card.id)
            if state is None or state.next_review_at is None or state.next_review_at <= today:
                due.append(card)
            if len(due) >= limit:
                break
        return due
