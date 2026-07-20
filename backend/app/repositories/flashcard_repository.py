import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import Flashcard
from app.models.curriculum import Subject, Topic
from app.models.progress import UserFlashcard


class FlashcardRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_with_names(self, *, topic_id: uuid.UUID | None = None) -> list[tuple[Flashcard, str, str]]:
        stmt = (
            select(Flashcard, Topic.name, Subject.name)
            .join(Topic, Flashcard.topic_id == Topic.id)
            .join(Subject, Topic.subject_id == Subject.id)
            .order_by(Subject.order_index, Topic.order_index, Flashcard.created_at)
        )
        if topic_id is not None:
            stmt = stmt.where(Flashcard.topic_id == topic_id)
        return [tuple(row) for row in self.db.execute(stmt).all()]

    def get_with_names(self, flashcard_id: uuid.UUID) -> tuple[Flashcard, str, str] | None:
        row = self.db.execute(
            select(Flashcard, Topic.name, Subject.name)
            .join(Topic, Flashcard.topic_id == Topic.id)
            .join(Subject, Topic.subject_id == Subject.id)
            .where(Flashcard.id == flashcard_id)
        ).first()
        return tuple(row) if row else None

    def user_states(self, user_id: uuid.UUID) -> dict[uuid.UUID, UserFlashcard]:
        return {
            r.flashcard_id: r
            for r in self.db.scalars(select(UserFlashcard).where(UserFlashcard.user_id == user_id)).all()
        }

    def get_or_create_state(self, user_id: uuid.UUID, flashcard_id: uuid.UUID) -> UserFlashcard:
        state = self.db.scalars(
            select(UserFlashcard).where(
                UserFlashcard.user_id == user_id, UserFlashcard.flashcard_id == flashcard_id
            )
        ).first()
        if state is None:
            state = UserFlashcard(user_id=user_id, flashcard_id=flashcard_id, box=1)
            self.db.add(state)
            self.db.flush()
        return state
