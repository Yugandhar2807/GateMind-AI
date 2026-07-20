"""
Ingest real GATE DA previous-year questions researched via a dedicated workflow
(see scripts/seed_data/research/pyq_questions.json). Every question was found and verified
by a research agent via WebSearch/WebFetch against GATE Overflow / official answer keys /
coaching post-exam analyses — never fabricated. Idempotent: skips a question if one with the
same question_markdown + topic already exists.

Difficulty wasn't part of the research schema (subjective, agents weren't asked for it) — we use
a simple, documented heuristic: 1-mark questions -> medium, 2-mark questions -> hard, matching the
general GATE convention that 2-mark questions are more involved. Refine via the admin panel later
if a question's actual difficulty diverges.

Usage:
    venv/Scripts/python.exe -m scripts.seed_pyq_questions
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.models.content import Subject, Topic  # noqa: E402
from app.models.enums import Difficulty, QuestionSource, QuestionType  # noqa: E402
from app.models.question import Question  # noqa: E402

DATA_FILE = Path(__file__).resolve().parent / "seed_data" / "research" / "pyq_questions.json"

DIFFICULTY_BY_MARKS = {1: Difficulty.MEDIUM, 2: Difficulty.HARD}
EXPECTED_TIME_BY_MARKS = {1: 90, 2: 150}
NEGATIVE_MARKS_MCQ = {1: 1 / 3, 2: 2 / 3}


def main() -> None:
    db = SessionLocal()
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            entries = json.load(f)

        total_created, total_skipped_dupe, total_missing_topic, total_bad_shape = 0, 0, 0, 0

        for entry in entries:
            year = entry.get("year")
            subject_name = entry.get("subject")
            subject = db.scalars(select(Subject).where(Subject.name == subject_name)).first()
            if subject is None:
                print(f"  WARNING: subject '{subject_name}' not found")
                continue

            for q in entry.get("questions", []):
                topic_name = q.get("topic_name")
                topic = db.scalars(
                    select(Topic).where(Topic.subject_id == subject.id, Topic.name == topic_name)
                ).first()
                if topic is None:
                    print(f"  WARNING: topic '{topic_name}' not found under '{subject_name}' ({year}), skipping question")
                    total_missing_topic += 1
                    continue

                try:
                    q_type = QuestionType(q["question_type"])
                    marks = int(q["marks"])
                except (KeyError, ValueError):
                    total_bad_shape += 1
                    continue

                existing = db.scalars(
                    select(Question).where(
                        Question.topic_id == topic.id,
                        Question.question_markdown == q["question_markdown"],
                    )
                ).first()
                if existing:
                    total_skipped_dupe += 1
                    continue

                options = q.get("options") or None
                correct_indices = q.get("correct_option_indices") or []
                correct_value = q.get("correct_value")
                tolerance = q.get("nat_tolerance") or None

                negative_marks = NEGATIVE_MARKS_MCQ.get(marks, 0.0) if q_type == QuestionType.MCQ else 0.0

                question = Question(
                    topic_id=topic.id,
                    question_type=q_type,
                    difficulty=DIFFICULTY_BY_MARKS.get(marks, Difficulty.MEDIUM),
                    source=QuestionSource.PYQ,
                    source_year=year,
                    question_markdown=q["question_markdown"],
                    options=options,
                    correct_answer={
                        "correct_option_indices": correct_indices,
                        "correct_value": correct_value if q_type == QuestionType.NAT else None,
                        "tolerance": tolerance,
                    },
                    nat_tolerance=tolerance,
                    explanation_markdown=q.get("explanation_markdown") or None,
                    marks=float(marks),
                    negative_marks=negative_marks,
                    expected_time_seconds=EXPECTED_TIME_BY_MARKS.get(marks, 90),
                )
                db.add(question)
                total_created += 1

            db.flush()

        db.commit()
        print(
            f"\nDone. {total_created} questions created, {total_skipped_dupe} duplicates skipped, "
            f"{total_missing_topic} topic mismatches, {total_bad_shape} malformed entries skipped."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
