"""
Seed flashcards from the same verified research used by scripts/seed.py, matching each
cheat-sheet bullet to the specific topic it's actually about (by word-overlap against topic
names) rather than duplicating every subject's cheat sheet onto all of its topics.

Bullets that don't look like real, self-contained concept/formula content (meta-commentary like
"scope boundary" or "time management rule of thumb") are skipped rather than seeded as fake
flashcards. Bullets that don't match any topic well fall back to that subject's highest-importance
topic, which is still a real, defensible placement — never a fabricated one.

Usage:
    venv/Scripts/python.exe -m scripts.seed_flashcards
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.models.content import Flashcard  # noqa: E402
from app.models.curriculum import Subject, Topic  # noqa: E402
from app.models.enums import Difficulty  # noqa: E402

RESEARCH_DIR = Path(__file__).resolve().parent / "seed_data" / "research"

SUBJECT_NAME_TO_FILE = {
    "Probability & Statistics": "subj_prob_stats.json",
    "Linear Algebra": "subj_linear_algebra.json",
    "Calculus & Optimization": "subj_calculus_optimization.json",
    "Programming, Data Structures & Algorithms": "subj_programming_dsa.json",
    "Database Management & Warehousing": "subj_dbms_warehousing.json",
    "Machine Learning": "subj_machine_learning.json",
    "Artificial Intelligence": "subj_ai.json",
    "General Aptitude": "subj_general_aptitude.json",
    "Deep Learning (MLP sub-topic)": "subj_deep_learning.json",
    "Data Science & Big Data Tools": "subj_data_science_bigdata.json",
}

_STOPWORDS = {"a", "an", "the", "of", "and", "or", "in", "on", "for", "to", "with", "vs", "is", "are", "&", "-", "on"}
_SKIP_TERM_PATTERNS = [
    "time management",
    "scope boundary",
    "key relationship",
    "for the ml-overlap",
    "supplementary",
]
_MIN_BULLET_LENGTH = 20


def _norm_words(text: str) -> set[str]:
    cleaned = re.sub(r"[^a-zA-Z0-9 ]", " ", text.lower())
    return {w for w in cleaned.split() if w not in _STOPWORDS and len(w) > 1}


def _extract_term(bullet: str) -> str:
    head = bullet[:100]
    if ":" in head:
        return bullet.split(":", 1)[0].strip()
    return bullet[:60].strip()


def _best_topic_match(term: str, topics: list[Topic]) -> tuple[Topic | None, int]:
    term_words = _norm_words(term)
    best, best_score = None, 0
    for topic in topics:
        score = len(term_words & _norm_words(topic.name))
        if score > best_score:
            best, best_score = topic, score
    return best, best_score


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.query(Flashcard).count()
        if existing > 0:
            print(f"Database already has {existing} flashcards — skipping seed (idempotent guard).")
            return

        total_created, total_skipped, total_fallback = 0, 0, 0

        for subject_name, filename in SUBJECT_NAME_TO_FILE.items():
            subject = db.scalars(select(Subject).where(Subject.name == subject_name)).first()
            if subject is None:
                print(f"  WARNING: subject '{subject_name}' not found in DB, skipping")
                continue

            topics = db.scalars(select(Topic).where(Topic.subject_id == subject.id)).all()
            if not topics:
                continue
            fallback_topic = max(topics, key=lambda t: (t.importance_1to5 or 0))

            with open(RESEARCH_DIR / filename, encoding="utf-8") as f:
                data = json.load(f)

            created_for_subject = 0
            for bullet in data.get("cheatSheet", []):
                if len(bullet) < _MIN_BULLET_LENGTH:
                    total_skipped += 1
                    continue
                term = _extract_term(bullet)
                if any(p in term.lower() or p in bullet[:120].lower() for p in _SKIP_TERM_PATTERNS):
                    total_skipped += 1
                    continue

                topic, score = _best_topic_match(term, topics)
                if topic is None or score == 0:
                    topic = fallback_topic
                    total_fallback += 1

                db.add(
                    Flashcard(
                        topic_id=topic.id,
                        front_md=term[:400],
                        back_md=bullet,
                        difficulty=Difficulty.MEDIUM,
                        source="cheat_sheet",
                    )
                )
                created_for_subject += 1
                total_created += 1

            print(f"  {subject_name}: {created_for_subject} flashcards")

        db.commit()
        print(f"\nDone. {total_created} flashcards created, {total_skipped} bullets skipped "
              f"(meta-commentary/too short), {total_fallback} used subject fallback topic.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
