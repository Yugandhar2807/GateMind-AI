import random
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.content import Topic
from app.models.enums import Difficulty
from app.models.mock import QuizAnswer, QuizAttempt
from app.models.question import Question


class PracticeRepository:
    def __init__(self, db: Session):
        self.db = db

    def select_questions(
        self,
        *,
        topic_id: int | None,
        subject_id: int | None,
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

        candidates = list(self.db.scalars(stmt).all())
        random.shuffle(candidates)
        return candidates[:count]

    def question_stats(self, topic_id: int) -> tuple[int, dict[str, int], dict[str, int]]:
        rows = self.db.scalars(select(Question).where(Question.topic_id == topic_id)).all()
        by_difficulty: dict[str, int] = {}
        by_type: dict[str, int] = {}
        for q in rows:
            by_difficulty[q.difficulty.value] = by_difficulty.get(q.difficulty.value, 0) + 1
            by_type[q.question_type.value] = by_type.get(q.question_type.value, 0) + 1
        return len(rows), by_difficulty, by_type

    def create_attempt(self, user_id: int, topic_id: int | None) -> QuizAttempt:
        attempt = QuizAttempt(user_id=user_id, topic_id=topic_id, started_at=datetime.utcnow(), is_complete=False)
        self.db.add(attempt)
        self.db.flush()
        return attempt

    def get_attempt(self, attempt_id: int, user_id: int) -> QuizAttempt | None:
        stmt = select(QuizAttempt).where(QuizAttempt.id == attempt_id, QuizAttempt.user_id == user_id)
        return self.db.scalars(stmt).first()

    def get_answer(self, attempt_id: int, question_id: int) -> QuizAnswer | None:
        stmt = select(QuizAnswer).where(QuizAnswer.attempt_id == attempt_id, QuizAnswer.question_id == question_id)
        return self.db.scalars(stmt).first()

    def list_attempts(self, user_id: int, limit: int = 20) -> list[QuizAttempt]:
        stmt = (
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.started_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
