import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.content import Flashcard
from app.models.enums import BookmarkType, Difficulty, SessionType
from app.models.progress import UserFlashcard
from app.models.user import User
from app.repositories.flashcard_repository import FlashcardRepository
from app.schemas.bookmark import BookmarkToggleRequest
from app.schemas.flashcard import FlashcardRead, FlashcardStateUpdate
from app.services.activity_service import record_activity
from app.services.bookmark_service import BookmarkService

BOX_INTERVAL_DAYS = {1: 1, 2: 3, 3: 7, 4: 15, 5: 30}
MAX_BOX = 5
DUE_LIMIT = 40


class FlashcardNotFoundError(Exception):
    pass


class FlashcardService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FlashcardRepository(db)

    def _bookmarked_ids(self, user_id: uuid.UUID) -> set[uuid.UUID]:
        return set(BookmarkService(self.db).bookmarked_target_ids(user_id, BookmarkType.FLASHCARD))

    def _read(
        self, card: Flashcard, topic_name: str, subject_name: str, state: UserFlashcard | None, bookmarked: set
    ) -> FlashcardRead:
        return FlashcardRead(
            id=card.id,
            topic_id=card.topic_id,
            topic_name=topic_name,
            subject_name=subject_name,
            front_markdown=card.front_md,
            back_markdown=card.back_md,
            difficulty=card.difficulty or Difficulty.MEDIUM,
            box=state.box if state else 1,
            is_bookmarked=card.id in bookmarked,
            is_favorite=state.is_favorite if state else False,
            review_later=state.review_later if state else False,
            next_review_at=state.next_review_at if state else None,
        )

    def list_all(self, user_id: uuid.UUID, *, topic_id: uuid.UUID | None = None) -> list[FlashcardRead]:
        rows = self.repo.list_with_names(topic_id=topic_id)
        states = self.repo.user_states(user_id)
        bookmarked = self._bookmarked_ids(user_id)
        return [self._read(c, tn, sn, states.get(c.id), bookmarked) for c, tn, sn in rows]

    def due_today(self, user_id: uuid.UUID, *, now: datetime) -> list[FlashcardRead]:
        rows = self.repo.list_with_names()
        states = self.repo.user_states(user_id)
        bookmarked = self._bookmarked_ids(user_id)
        out: list[FlashcardRead] = []
        for c, tn, sn in rows:
            st = states.get(c.id)
            if st is None or st.next_review_at is None or st.next_review_at <= now:
                out.append(self._read(c, tn, sn, st, bookmarked))
            if len(out) >= DUE_LIMIT:
                break
        return out

    def review(self, user: User, flashcard_id: uuid.UUID, *, correct: bool, now: datetime) -> FlashcardRead:
        row = self.repo.get_with_names(flashcard_id)
        if row is None:
            raise FlashcardNotFoundError(flashcard_id)
        card, tn, sn = row
        state = self.repo.get_or_create_state(user.id, flashcard_id)
        state.box = min(state.box + 1, MAX_BOX) if correct else 1
        state.next_review_at = now + timedelta(days=BOX_INTERVAL_DAYS[state.box])
        state.last_reviewed_at = now
        state.times_reviewed += 1
        if correct:
            state.times_correct += 1
        record_activity(self.db, user, minutes=0, session_type=SessionType.FLASHCARDS, topic_id=card.topic_id)
        self.db.commit()
        self.db.refresh(state)
        return self._read(card, tn, sn, state, self._bookmarked_ids(user.id))

    def update_state(self, user: User, flashcard_id: uuid.UUID, payload: FlashcardStateUpdate) -> FlashcardRead:
        row = self.repo.get_with_names(flashcard_id)
        if row is None:
            raise FlashcardNotFoundError(flashcard_id)
        card, tn, sn = row
        state = self.repo.get_or_create_state(user.id, flashcard_id)
        data = payload.model_dump(exclude_unset=True)
        if "is_favorite" in data:
            state.is_favorite = data["is_favorite"]
        if "review_later" in data:
            state.review_later = data["review_later"]
        self.db.commit()
        # is_bookmarked lives in the generic bookmark system (BookmarkType.FLASHCARD).
        if "is_bookmarked" in data:
            currently = card.id in self._bookmarked_ids(user.id)
            if bool(data["is_bookmarked"]) != currently:
                BookmarkService(self.db).toggle(
                    user.id, BookmarkToggleRequest(bookmark_type=BookmarkType.FLASHCARD, target_id=card.id)
                )
        self.db.refresh(state)
        return self._read(card, tn, sn, state, self._bookmarked_ids(user.id))
