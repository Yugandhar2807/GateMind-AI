"""
Seed a curated starter set of GATE-DA practice questions (scripts/seed_data/practice_questions.json)
into the normalized questions + question_options tables. These are hand-verified, unambiguous
conceptual questions labelled source=practice (NOT claimed to be official PYQs). A full verified
PYQ bank is a separate curation effort. Idempotent per (topic, question text).

Usage:
    venv/Scripts/python.exe -m scripts.seed_practice_questions
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.models.content import Question, QuestionOption  # noqa: E402
from app.models.curriculum import Subject, Topic  # noqa: E402
from app.models.enums import Difficulty, QuestionSource, QuestionType  # noqa: E402

DATA_FILE = Path(__file__).resolve().parent / "seed_data" / "practice_questions.json"
NEG_MCQ = {1: 1 / 3, 2: 2 / 3}
EXPECTED_TIME = {1: 90, 2: 150}


def main() -> None:
    db = SessionLocal()
    try:
        blocks = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        created = skipped = missing = 0

        for block in blocks:
            subject = db.scalars(select(Subject).where(Subject.name == block["subject"])).first()
            if subject is None:
                print(f"  WARN subject not found: {block['subject']}")
                continue

            for q in block["questions"]:
                topic = db.scalars(
                    select(Topic).where(Topic.subject_id == subject.id, Topic.name == q["topic_name"])
                ).first()
                if topic is None:
                    print(f"  WARN topic not found: {q['topic_name']}")
                    missing += 1
                    continue

                exists = db.scalars(
                    select(Question).where(
                        Question.topic_id == topic.id, Question.question_md == q["question_markdown"]
                    )
                ).first()
                if exists:
                    skipped += 1
                    continue

                qtype = QuestionType(q["question_type"])
                marks = int(q["marks"])
                tags = (
                    {"nat_tolerance": q["nat_tolerance"]}
                    if qtype == QuestionType.NAT and "nat_tolerance" in q
                    else None
                )
                question = Question(
                    topic_id=topic.id,
                    type=qtype,
                    difficulty=Difficulty(q.get("difficulty", "medium")),
                    source=QuestionSource.PRACTICE,
                    source_year=None,
                    question_md=q["question_markdown"],
                    explanation_md=q.get("explanation_markdown"),
                    correct_value=str(q["correct_value"]) if "correct_value" in q else None,
                    marks=float(marks),
                    negative_marks=(NEG_MCQ.get(marks, 0.0) if qtype == QuestionType.MCQ else 0.0),
                    expected_time_seconds=EXPECTED_TIME.get(marks, 90),
                    tags=tags,
                )
                db.add(question)
                db.flush()

                correct = set(q.get("correct_option_indices", []))
                for i, opt in enumerate(q.get("options", []) or []):
                    db.add(
                        QuestionOption(
                            question_id=question.id,
                            label=chr(65 + i),
                            option_md=opt,
                            is_correct=(i in correct),
                            order_index=i,
                        )
                    )
                created += 1

        db.commit()
        print(f"Practice questions: {created} created, {skipped} duplicates, {missing} topic mismatches.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
