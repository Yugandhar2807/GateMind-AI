import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Attempt, AttemptAnswer
from app.models.content import Question, QuestionOption
from app.models.curriculum import Topic
from app.models.enums import AttemptStatus, AttemptType, Difficulty


class PracticeRepository:
    def __init__(self, db: Session):
        self.db = db

    def select_questions(
        self,
        *,
        topic_id: uuid.UUID | None,
        subject_id: uuid.UUID | None,
        difficulty: Difficulty | None,
        count: int,
    ) -> list[Question]:
        stmt = select(Question)
        if topic_id is not None:
            stmt = stmt.where(Question.topic_id == topic_id)
        elif subject_id is not None:
            stmt = stmt.join(Topic, Question.topic_id == Topic.id).where(Topic.subject_id == subject_id)
        if difficulty is not None:
            stmt = stmt.where(Question.difficulty == difficulty)
        # Deterministic-but-varied: order by created_at; caller trims to count.
        candidates = list(self.db.scalars(stmt.order_by(Question.created_at)).all())
        return candidates[:count]

    def options_for(self, question_ids: list[uuid.UUID]) -> dict[uuid.UUID, list[QuestionOption]]:
        if not question_ids:
            return {}
        rows = self.db.scalars(
            select(QuestionOption)
            .where(QuestionOption.question_id.in_(question_ids))
            .order_by(QuestionOption.order_index)
        ).all()
        out: dict[uuid.UUID, list[QuestionOption]] = {}
        for o in rows:
            out.setdefault(o.question_id, []).append(o)
        return out

    def question_stats(self, topic_id: uuid.UUID) -> tuple[int, dict[str, int], dict[str, int]]:
        rows = self.db.scalars(select(Question).where(Question.topic_id == topic_id)).all()
        by_difficulty: dict[str, int] = {}
        by_type: dict[str, int] = {}
        for q in rows:
            by_difficulty[q.difficulty.value] = by_difficulty.get(q.difficulty.value, 0) + 1
            by_type[q.type.value] = by_type.get(q.type.value, 0) + 1
        return len(rows), by_difficulty, by_type

    def create_attempt(self, user_id: uuid.UUID, topic_id: uuid.UUID | None, subject_id: uuid.UUID | None) -> Attempt:
        attempt = Attempt(
            user_id=user_id,
            attempt_type=AttemptType.PRACTICE,
            topic_id=topic_id,
            subject_id=subject_id,
            status=AttemptStatus.IN_PROGRESS,
        )
        self.db.add(attempt)
        self.db.flush()
        return attempt

    def get_attempt(self, attempt_id: uuid.UUID, user_id: uuid.UUID) -> Attempt | None:
        return self.db.scalars(
            select(Attempt).where(Attempt.id == attempt_id, Attempt.user_id == user_id)
        ).first()

    def get_answer(self, attempt_id: uuid.UUID, question_id: uuid.UUID) -> AttemptAnswer | None:
        return self.db.scalars(
            select(AttemptAnswer).where(
                AttemptAnswer.attempt_id == attempt_id, AttemptAnswer.question_id == question_id
            )
        ).first()

    def list_answers(self, attempt_id: uuid.UUID) -> list[AttemptAnswer]:
        return list(
            self.db.scalars(select(AttemptAnswer).where(AttemptAnswer.attempt_id == attempt_id)).all()
        )
