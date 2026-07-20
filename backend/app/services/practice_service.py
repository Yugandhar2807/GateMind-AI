import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import AttemptAnswer
from app.models.content import Question, QuestionOption
from app.models.enums import AttemptStatus, ProgressStatus, QuestionSource, QuestionType, SessionType
from app.models.progress import UserTopicProgress
from app.models.user import User
from app.repositories.practice_repository import PracticeRepository
from app.schemas.practice import (
    PracticeAnswerRequest,
    PracticeAnswerResult,
    PracticeAttemptStarted,
    PracticeStartRequest,
    PracticeSubmitResponse,
    QuestionPublic,
    TopicQuestionStats,
)
from app.services.activity_service import record_activity


class AttemptNotFoundError(Exception):
    pass


class QuestionNotFoundError(Exception):
    pass


def _correct_indices(options: list[QuestionOption]) -> list[int]:
    return [i for i, o in enumerate(sorted(options, key=lambda x: x.order_index)) if o.is_correct]


class PracticeService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PracticeRepository(db)

    def topic_stats(self, topic_id: uuid.UUID) -> TopicQuestionStats:
        total, by_difficulty, by_type = self.repo.question_stats(topic_id)
        return TopicQuestionStats(total=total, by_difficulty=by_difficulty, by_type=by_type)

    def start(self, user_id: uuid.UUID, payload: PracticeStartRequest) -> PracticeAttemptStarted:
        questions = self.repo.select_questions(
            topic_id=payload.topic_id,
            subject_id=payload.subject_id,
            difficulty=payload.difficulty,
            count=max(1, min(payload.question_count, 50)),
        )
        options = self.repo.options_for([q.id for q in questions])
        attempt = self.repo.create_attempt(user_id, payload.topic_id, payload.subject_id)
        self.db.commit()

        public = []
        for q in questions:
            opts = sorted(options.get(q.id, []), key=lambda x: x.order_index)
            public.append(
                QuestionPublic(
                    id=q.id,
                    topic_id=q.topic_id,
                    question_type=q.type,
                    difficulty=q.difficulty,
                    source=q.source,
                    source_year=q.source_year,
                    question_markdown=q.question_md,
                    options=[o.option_md for o in opts] if opts else None,
                    marks=q.marks,
                    negative_marks=q.negative_marks,
                    expected_time_seconds=q.expected_time_seconds,
                )
            )
        return PracticeAttemptStarted(attempt_id=attempt.id, topic_id=payload.topic_id, questions=public)

    def answer(
        self, user_id: uuid.UUID, attempt_id: uuid.UUID, payload: PracticeAnswerRequest
    ) -> PracticeAnswerResult:
        attempt = self.repo.get_attempt(attempt_id, user_id)
        if attempt is None:
            raise AttemptNotFoundError(attempt_id)
        question = self.db.get(Question, payload.question_id)
        if question is None:
            raise QuestionNotFoundError(payload.question_id)

        options = self.repo.options_for([question.id]).get(question.id, [])
        correct_indices = _correct_indices(options)
        correct_value = float(question.correct_value) if question.correct_value else None
        tolerance = float((question.tags or {}).get("nat_tolerance") or 0.0) if isinstance(question.tags, dict) else 0.0

        is_correct: bool | None = None
        marks_awarded = 0.0
        if payload.is_skipped:
            is_correct = None
        elif question.type == QuestionType.MCQ:
            selected = payload.selected_indices or []
            is_correct = len(selected) == 1 and selected[0] in correct_indices
            marks_awarded = question.marks if is_correct else -question.negative_marks
        elif question.type == QuestionType.MSQ:
            is_correct = set(payload.selected_indices or []) == set(correct_indices)
            marks_awarded = question.marks if is_correct else 0.0
        elif question.type == QuestionType.NAT:
            is_correct = (
                payload.nat_value is not None
                and correct_value is not None
                and abs(payload.nat_value - correct_value) <= tolerance
            )
            marks_awarded = question.marks if is_correct else 0.0

        existing = self.repo.get_answer(attempt_id, question.id)
        if existing:
            existing.selected_option_ids = payload.selected_indices
            existing.nat_value = str(payload.nat_value) if payload.nat_value is not None else None
            existing.is_correct = is_correct
            existing.is_skipped = payload.is_skipped
            existing.time_taken_seconds = payload.time_taken_seconds
            existing.marks_awarded = marks_awarded
        else:
            self.db.add(
                AttemptAnswer(
                    attempt_id=attempt_id,
                    question_id=question.id,
                    selected_option_ids=payload.selected_indices,
                    nat_value=str(payload.nat_value) if payload.nat_value is not None else None,
                    is_correct=is_correct,
                    is_skipped=payload.is_skipped,
                    marks_awarded=marks_awarded,
                    time_taken_seconds=payload.time_taken_seconds,
                )
            )
        self.db.commit()

        return PracticeAnswerResult(
            question_id=question.id,
            is_correct=is_correct,
            marks_awarded=marks_awarded,
            correct_option_indices=correct_indices,
            correct_value=correct_value,
            explanation_markdown=question.explanation_md,
        )

    def submit(self, user: User, attempt_id: uuid.UUID) -> PracticeSubmitResponse:
        attempt = self.repo.get_attempt(attempt_id, user.id)
        if attempt is None:
            raise AttemptNotFoundError(attempt_id)

        answers = self.repo.list_answers(attempt_id)
        questions = {
            q.id: q
            for q in self.db.scalars(
                select(Question).where(Question.id.in_([a.question_id for a in answers]))
            ).all()
        }

        correct_count = sum(1 for a in answers if a.is_correct is True)
        incorrect_count = sum(1 for a in answers if a.is_correct is False and not a.is_skipped)
        skipped_count = sum(1 for a in answers if a.is_skipped)
        attempted = correct_count + incorrect_count
        score = sum(a.marks_awarded or 0.0 for a in answers)
        max_score = sum(q.marks for q in questions.values())
        negative_marks_lost = sum(-(a.marks_awarded or 0) for a in answers if (a.marks_awarded or 0) < 0)
        accuracy = round(100 * correct_count / attempted, 1) if attempted else 0.0
        avg_time = round(sum(a.time_taken_seconds or 0 for a in answers) / len(answers), 1) if answers else 0.0

        attempt.status = AttemptStatus.SUBMITTED
        attempt.submitted_at = datetime.now(timezone.utc)
        attempt.score = score
        attempt.max_score = max_score
        attempt.accuracy_percent = accuracy
        attempt.correct_count = correct_count
        attempt.incorrect_count = incorrect_count
        attempt.skipped_count = skipped_count
        attempt.negative_marks_lost = negative_marks_lost
        attempt.duration_seconds = sum(a.time_taken_seconds or 0 for a in answers)

        self._update_topic_progress(user.id, answers, questions)
        total_minutes = max(1, round(sum(a.time_taken_seconds or 0 for a in answers) / 60))
        record_activity(self.db, user, minutes=total_minutes, session_type=SessionType.PRACTICE, topic_id=attempt.topic_id)
        self.db.commit()

        return PracticeSubmitResponse(
            attempt_id=attempt.id,
            score=score,
            max_score=max_score,
            accuracy_percent=accuracy,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            skipped_count=skipped_count,
            negative_marks_lost=negative_marks_lost,
            avg_time_per_question_seconds=avg_time,
        )

    def _update_topic_progress(self, user_id, answers, questions) -> None:
        """Roll practice accuracy into each topic's progress → powers the Dashboard weak/strong widget."""
        by_topic: dict[uuid.UUID, list] = {}
        for a in answers:
            q = questions.get(a.question_id)
            if q is not None:
                by_topic.setdefault(q.topic_id, []).append(a)

        for topic_id, topic_answers in by_topic.items():
            progress = self.db.scalars(
                select(UserTopicProgress).where(
                    UserTopicProgress.user_id == user_id, UserTopicProgress.topic_id == topic_id
                )
            ).first()
            if progress is None:
                progress = UserTopicProgress(
                    user_id=user_id, topic_id=topic_id, status=ProgressStatus.IN_PROGRESS
                )
                self.db.add(progress)
                self.db.flush()

            attempted = [a for a in topic_answers if not a.is_skipped]
            correct = [a for a in attempted if a.is_correct]
            pyq_correct = [a for a in correct if questions[a.question_id].source == QuestionSource.PYQ]

            prior_attempted = progress.practice_solved
            prior_correct_est = round((progress.accuracy_percent or 0) / 100 * prior_attempted)
            progress.practice_solved += len(attempted)
            progress.pyqs_solved += len(pyq_correct)
            total_attempted = prior_attempted + len(attempted)
            total_correct = prior_correct_est + len(correct)
            progress.accuracy_percent = (
                round(100 * total_correct / total_attempted, 1) if total_attempted else None
            )
            progress.last_studied_at = datetime.now(timezone.utc)
