from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import ProgressStatus, QuestionSource, QuestionType, SessionType
from app.models.mock import QuizAnswer, QuizAttempt
from app.models.progress import UserTopicProgress
from app.models.question import Question
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


class QuestionNotInAttemptError(Exception):
    pass


class PracticeService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PracticeRepository(db)

    def topic_stats(self, topic_id: int) -> TopicQuestionStats:
        total, by_difficulty, by_type = self.repo.question_stats(topic_id)
        return TopicQuestionStats(total=total, by_difficulty=by_difficulty, by_type=by_type)

    def start(self, user_id: int, payload: PracticeStartRequest) -> PracticeAttemptStarted:
        questions = self.repo.select_questions(
            topic_id=payload.topic_id,
            subject_id=payload.subject_id,
            difficulty=payload.difficulty,
            count=max(1, min(payload.question_count, 50)),
        )
        attempt = self.repo.create_attempt(user_id, payload.topic_id)
        self.db.commit()

        return PracticeAttemptStarted(
            attempt_id=attempt.id,
            topic_id=payload.topic_id,
            questions=[QuestionPublic.model_validate(q) for q in questions],
        )

    def answer(self, user_id: int, attempt_id: int, payload: PracticeAnswerRequest) -> PracticeAnswerResult:
        attempt = self.repo.get_attempt(attempt_id, user_id)
        if attempt is None:
            raise AttemptNotFoundError(attempt_id)

        question = self.db.get(Question, payload.question_id)
        if question is None:
            raise QuestionNotInAttemptError(payload.question_id)

        correct = question.correct_answer or {}
        correct_indices = correct.get("correct_option_indices", [])
        correct_value = correct.get("correct_value")
        tolerance = correct.get("tolerance") or question.nat_tolerance or 0.0

        is_correct: bool | None = None
        marks_awarded = 0.0

        if payload.is_skipped:
            is_correct = None
        elif question.question_type == QuestionType.MCQ:
            selected = payload.selected_indices or []
            is_correct = len(selected) == 1 and selected[0] in correct_indices
            marks_awarded = question.marks if is_correct else -question.negative_marks
        elif question.question_type == QuestionType.MSQ:
            selected_set = set(payload.selected_indices or [])
            is_correct = selected_set == set(correct_indices)
            marks_awarded = question.marks if is_correct else 0.0
        elif question.question_type == QuestionType.NAT:
            if payload.nat_value is not None and correct_value is not None:
                is_correct = abs(payload.nat_value - correct_value) <= (tolerance or 0.0)
            else:
                is_correct = False
            marks_awarded = question.marks if is_correct else 0.0

        existing = self.repo.get_answer(attempt_id, payload.question_id)
        user_answer_json = {"selected_indices": payload.selected_indices, "nat_value": payload.nat_value}
        if existing:
            existing.user_answer = user_answer_json
            existing.is_correct = is_correct
            existing.is_skipped = payload.is_skipped
            existing.time_taken_seconds = payload.time_taken_seconds
            existing.marks_awarded = marks_awarded
        else:
            self.db.add(
                QuizAnswer(
                    attempt_id=attempt_id,
                    question_id=payload.question_id,
                    user_answer=user_answer_json,
                    is_correct=is_correct,
                    is_skipped=payload.is_skipped,
                    time_taken_seconds=payload.time_taken_seconds,
                    marks_awarded=marks_awarded,
                )
            )
        self.db.commit()

        return PracticeAnswerResult(
            question_id=question.id,
            is_correct=is_correct,
            marks_awarded=marks_awarded,
            correct_option_indices=correct_indices,
            correct_value=correct_value,
            explanation_markdown=question.explanation_markdown,
        )

    def submit(self, user: User, attempt_id: int) -> PracticeSubmitResponse:
        attempt = self.repo.get_attempt(attempt_id, user.id)
        if attempt is None:
            raise AttemptNotFoundError(attempt_id)

        answers = list(
            self.db.scalars(select(QuizAnswer).where(QuizAnswer.attempt_id == attempt_id)).all()
        )
        questions_by_id = {
            q.id: q for q in self.db.scalars(select(Question).where(Question.id.in_([a.question_id for a in answers]))).all()
        }

        correct_count = sum(1 for a in answers if a.is_correct is True)
        incorrect_count = sum(1 for a in answers if a.is_correct is False and not a.is_skipped)
        skipped_count = sum(1 for a in answers if a.is_skipped)
        attempted = correct_count + incorrect_count

        score = sum(a.marks_awarded or 0.0 for a in answers)
        max_score = sum(q.marks for q in questions_by_id.values())
        negative_marks_lost = sum(-a.marks_awarded for a in answers if (a.marks_awarded or 0) < 0)
        accuracy = round(100 * correct_count / attempted, 1) if attempted else 0.0
        avg_time = round(sum(a.time_taken_seconds or 0 for a in answers) / len(answers), 1) if answers else 0.0

        attempt.submitted_at = datetime.utcnow()
        attempt.score = score
        attempt.accuracy_percent = accuracy
        attempt.avg_time_per_question_seconds = avg_time
        attempt.negative_marks_lost = negative_marks_lost
        attempt.is_complete = True

        self._update_topic_progress(user.id, answers, questions_by_id)

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

    def _update_topic_progress(self, user_id: int, answers: list[QuizAnswer], questions_by_id: dict[int, Question]) -> None:
        """Roll practice results into each affected topic's UserTopicProgress, so the Dashboard's
        weak/strong-topics and accuracy widgets (built in Phase 2, honestly empty until now) get
        real data."""
        by_topic: dict[int, list[QuizAnswer]] = {}
        for a in answers:
            q = questions_by_id.get(a.question_id)
            if q is None:
                continue
            by_topic.setdefault(q.topic_id, []).append(a)

        for topic_id, topic_answers in by_topic.items():
            progress = self.db.scalars(
                select(UserTopicProgress).where(
                    UserTopicProgress.user_id == user_id, UserTopicProgress.topic_id == topic_id
                )
            ).first()
            if progress is None:
                progress = UserTopicProgress(user_id=user_id, topic_id=topic_id, status=ProgressStatus.IN_PROGRESS)
                self.db.add(progress)
                self.db.flush()

            attempted = [a for a in topic_answers if not a.is_skipped]
            correct = [a for a in attempted if a.is_correct]
            pyq_correct = [
                a for a in correct if questions_by_id[a.question_id].source == QuestionSource.PYQ
            ]

            progress.practice_solved += len(attempted)
            progress.pyqs_solved += len(pyq_correct)

            # Rolling accuracy across all practice on this topic (not just this session).
            prior_attempted = max(0, progress.practice_solved - len(attempted))
            prior_correct_est = round((progress.accuracy_percent or 0) / 100 * prior_attempted)
            total_attempted = prior_attempted + len(attempted)
            total_correct = prior_correct_est + len(correct)
            progress.accuracy_percent = round(100 * total_correct / total_attempted, 1) if total_attempted else None
            progress.last_studied_at = datetime.utcnow()
