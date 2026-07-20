"""
Normalize the GATE-DA-2027 research (scripts/seed_data/research/*.json) into the Postgres
curriculum: subjects, topics (+ subtopics), the prerequisite dependency graph, and resources
(subject-wide + curated topic-specific). Postgres is the single source of truth — the frontend
never hardcodes syllabus data.

Idempotent: skips if subjects already exist. Never fabricates a URL (only populates `url` when
an explicit link was present in the researched text).

Usage:
    venv/Scripts/python.exe -m scripts.seed_content
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parents[1]))

from slugify import slugify  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.models.curriculum import Resource, Subject, Topic, TopicPrerequisite, TopicResource  # noqa: E402
from app.models.enums import Difficulty, NodeLevel, PriorityLevel, ResourceLevel, ResourceType  # noqa: E402

RESEARCH_DIR = Path(__file__).resolve().parent / "seed_data" / "research"

SUBJECT_FILES = [
    {"file": "subj_prob_stats.json", "name": "Probability & Statistics", "is_official": True},
    {"file": "subj_linear_algebra.json", "name": "Linear Algebra", "is_official": True},
    {"file": "subj_calculus_optimization.json", "name": "Calculus & Optimization", "is_official": True},
    {"file": "subj_programming_dsa.json", "name": "Programming, Data Structures & Algorithms", "is_official": True},
    {"file": "subj_dbms_warehousing.json", "name": "Database Management & Warehousing", "is_official": True},
    {"file": "subj_machine_learning.json", "name": "Machine Learning", "is_official": True},
    {"file": "subj_ai.json", "name": "Artificial Intelligence", "is_official": True},
    {"file": "subj_general_aptitude.json", "name": "General Aptitude", "is_official": True},
    {"file": "subj_deep_learning.json", "name": "Deep Learning (MLP sub-topic)", "is_official": False},
    {"file": "subj_data_science_bigdata.json", "name": "Data Science & Big Data Tools", "is_official": False},
]

# Transparent heuristic (research gives difficulty1to5, not hours). Documented in docs/DATABASE.md.
_HOURS_BY_DIFFICULTY = {1: 2.0, 2: 3.0, 3: 5.0, 4: 7.0, 5: 10.0}
_REVISION_BY_IMPORTANCE = {5: "weekly", 4: "biweekly", 3: "monthly", 2: "6-weekly", 1: "as-needed"}

_DIFFICULTY_KEYWORDS = [
    (Difficulty.VERY_HARD, ["very hard", "toughest"]),
    (Difficulty.HARD, ["hard", "difficult", "high"]),
    (Difficulty.MEDIUM, ["moderate", "medium"]),
    (Difficulty.EASY, ["easy", "low"]),
]
_PRIORITY_KEYWORDS = [
    (PriorityLevel.HIGH, ["high"]),
    (PriorityLevel.MEDIUM, ["medium", "moderate"]),
    (PriorityLevel.LOW, ["low"]),
]

_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.(?:com|org|in|edu|net|io|ac\.in|co\.in)"
    r"(?:/[\w\-./?=&%#]*)?)"
)
_PLATFORM_RULES = [
    (ResourceType.LECTURE_SERIES, ResourceLevel.INTERMEDIATE, "MIT OCW", ["mit ocw", "ocw.mit.edu", "opencourseware"]),
    (ResourceType.LECTURE_SERIES, ResourceLevel.INTERMEDIATE, "NPTEL", ["nptel"]),
    (ResourceType.GITHUB_REPO, ResourceLevel.INTERMEDIATE, "GitHub", ["github.com", "github repo", "/github"]),
    (ResourceType.VIDEO, ResourceLevel.BEGINNER, "YouTube", ["youtube", "3blue1brown", "youtu.be"]),
    (ResourceType.DOCUMENTATION, ResourceLevel.BEGINNER, "GeeksforGeeks", ["geeksforgeeks"]),
    (ResourceType.DOCUMENTATION, ResourceLevel.INTERMEDIATE, "GATE Overflow", ["gateoverflow", "gate overflow"]),
    (ResourceType.RESEARCH_PAPER, ResourceLevel.RESEARCH, "arXiv", ["arxiv"]),
    (ResourceType.LECTURE_SERIES, ResourceLevel.INTERMEDIATE, "Coursera", ["coursera"]),
    (ResourceType.LECTURE_SERIES, ResourceLevel.INTERMEDIATE, "edX", ["edx"]),
    (ResourceType.ARTICLE, ResourceLevel.BEGINNER, "Analytics Vidhya", ["analytics vidhya"]),
]
_HEADLINE_WINDOW = 120
_BOOK_PATTERN = re.compile(
    r"^[A-Z][A-Za-z.]+(?:\s[A-Z][A-Za-z.]+){0,4}(?:,\s[A-Z][A-Za-z.]+(?:\s[A-Z][A-Za-z.]+){0,3})*,\s*['\"]"
)


def classify_resource(text: str) -> tuple[ResourceType, ResourceLevel, str | None]:
    if _BOOK_PATTERN.match(text):
        return ResourceType.BOOK, ResourceLevel.INTERMEDIATE, None
    headline = text[:_HEADLINE_WINDOW].lower()
    for r_type, level, platform, keywords in _PLATFORM_RULES:
        if any(kw in headline for kw in keywords):
            return r_type, level, platform
    lower = text.lower()
    for r_type, level, platform, keywords in _PLATFORM_RULES:
        if any(kw in lower for kw in keywords):
            return r_type, level, platform
    return ResourceType.ARTICLE, ResourceLevel.INTERMEDIATE, None


def extract_url(text: str) -> str | None:
    match = _URL_RE.search(text)
    return f"https://{match.group(1)}" if match else None


def extract_title(text: str) -> str:
    for sep in [" — ", " – ", ": ", " (the ", ". "]:
        if sep in text:
            candidate = text.split(sep)[0].strip()
            if 8 <= len(candidate) <= 140:
                return candidate
    return text[:140].rsplit(" ", 1)[0] if len(text) > 140 else text


def infer_from_keywords(text: str, rules: list, default):
    lower = (text or "").lower()
    for value, keywords in rules:
        if any(kw in lower for kw in keywords):
            return value
    return default


def int_to_difficulty(value: int | None) -> Difficulty | None:
    if value is None:
        return None
    return {1: Difficulty.EASY, 2: Difficulty.EASY, 3: Difficulty.MEDIUM, 4: Difficulty.HARD, 5: Difficulty.VERY_HARD}.get(
        value, Difficulty.MEDIUM
    )


def parse_weightage(text: str) -> tuple[float | None, float | None]:
    range_match = re.search(r"(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)\s*%", text or "")
    if range_match:
        return float(range_match.group(1)), float(range_match.group(2))
    single = re.search(r"(\d+(?:\.\d+)?)\s*%", text or "")
    v = float(single.group(1)) if single else None
    return v, v


def subject_description_md(data: dict, entry: dict) -> str | None:
    parts = []
    if not entry["is_official"] and data.get("subject") != entry["name"]:
        parts.append(f"> {data['subject']}")
    if data.get("weightagePercent"):
        parts.append(f"**Weightage:** {data['weightagePercent']}")
    if data.get("difficulty"):
        parts.append(f"**Difficulty:** {data['difficulty']}")
    if data.get("priorityForTopRank"):
        parts.append(f"**Priority for a top rank:** {data['priorityForTopRank']}")
    if data.get("pyqTrendByYear"):
        parts.append(f"**PYQ trend (2024-2026):** {data['pyqTrendByYear']}")
    if data.get("expected2027"):
        parts.append(f"**2027 expectation:** {data['expected2027']}")
    return "\n\n".join(parts) or None


def unique_slug(base: str, seen: set[str]) -> str:
    slug = slugify(base)[:158]
    candidate, n = slug, 1
    while candidate in seen:
        candidate = f"{slug[:150]}-{n}"
        n += 1
    seen.add(candidate)
    return candidate


def main() -> None:
    db: Session = SessionLocal()
    try:
        if db.scalar(select(Subject).limit(1)) is not None:
            print("Subjects already present — skipping content seed (idempotent guard).")
            return

        topic_slugs: set[str] = set()
        # (topic, [prerequisite names]) collected for a second pass once all names exist.
        prereq_work: list[tuple[Topic, list[str]]] = []
        name_to_topic: dict[str, Topic] = {}

        n_subjects = n_topics = n_resources = n_edges = 0

        for order, entry in enumerate(SUBJECT_FILES):
            data = json.loads((RESEARCH_DIR / entry["file"]).read_text(encoding="utf-8"))
            w_min, w_max = parse_weightage(data.get("weightagePercent", ""))
            subject = Subject(
                slug=slugify(entry["name"])[:120],
                name=entry["name"],
                description=subject_description_md(data, entry),
                weightage_min_percent=w_min,
                weightage_max_percent=w_max,
                difficulty=infer_from_keywords(data.get("difficulty", ""), _DIFFICULTY_KEYWORDS, Difficulty.MEDIUM),
                priority=infer_from_keywords(data.get("priorityForTopRank", ""), _PRIORITY_KEYWORDS, PriorityLevel.MEDIUM),
                order_index=order,
                is_official_section=entry["is_official"],
            )
            db.add(subject)
            db.flush()
            n_subjects += 1

            cheat_md = "\n".join(f"- {c}" for c in data.get("cheatSheet", [])) or None
            mistakes_md = "\n".join(f"- {m}" for m in data.get("commonMistakes", [])) or None

            subject_topics: list[Topic] = []
            for i, sub in enumerate(data.get("subtopics", [])):
                diff1to5 = sub.get("difficulty1to5")
                topic = Topic(
                    subject_id=subject.id,
                    parent_topic_id=None,
                    slug=unique_slug(f"{subject.slug}-{sub['name']}", topic_slugs),
                    name=sub["name"],
                    level=NodeLevel.TOPIC,
                    order_index=i,
                    difficulty=int_to_difficulty(diff1to5),
                    importance_1to5=sub.get("importance1to5"),
                    pyq_frequency=sub.get("pyqFrequency"),
                    estimated_hours=_HOURS_BY_DIFFICULTY.get(diff1to5 or 3, 5.0),
                    revision_frequency=_REVISION_BY_IMPORTANCE.get(sub.get("importance1to5") or 3),
                    prerequisites_text=", ".join(sub.get("prerequisites") or []) or None,
                    # Subject-level cheat sheet / mistakes (research granularity); shown on the Topic Page.
                    cheat_sheet_md=cheat_md,
                    common_mistakes_md=mistakes_md,
                )
                db.add(topic)
                db.flush()
                subject_topics.append(topic)
                name_to_topic[sub["name"].strip()] = topic
                prereq_work.append((topic, sub.get("prerequisites") or []))
                n_topics += 1

            # Subject-wide resources → linked to every topic in the subject (rank 0..N).
            for raw in data.get("booksAndResources", []):
                r_type, level, platform = classify_resource(raw)
                resource = Resource(
                    type=r_type,
                    title=extract_title(raw),
                    url=extract_url(raw),
                    provider=platform,
                    description=raw,
                    level=level,
                    is_free=True,
                )
                db.add(resource)
                db.flush()
                n_resources += 1
                for rank, topic in enumerate(subject_topics):
                    db.add(TopicResource(topic_id=topic.id, resource_id=resource.id, relevance_rank=rank))

        # Second pass: prerequisite dependency-graph edges (match prereq names to real topics).
        for topic, prereq_names in prereq_work:
            for name in prereq_names:
                pre = name_to_topic.get(name.strip())
                if pre is not None and pre.id != topic.id:
                    db.add(TopicPrerequisite(topic_id=topic.id, prerequisite_topic_id=pre.id))
                    n_edges += 1

        db.commit()
        print(
            f"Seeded: {n_subjects} subjects, {n_topics} topics, {n_resources} subject-wide resources, "
            f"{n_edges} prerequisite edges."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
