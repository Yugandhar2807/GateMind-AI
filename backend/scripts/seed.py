"""
Seed the database from the GATE DA research gathered 2026-07-17 (20 independent research
agents cross-checking official GATE portals — see scripts/seed_data/research/*.json).

Rule followed throughout: never fabricate a URL. A resource's `url` is only populated when
an explicit URL-like substring was present in the researched text; otherwise it is left null
and the full original description is preserved so a human can add a link via the admin panel.

Usage:
    venv/Scripts/python.exe -m scripts.seed
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parents[1]))

from slugify import slugify  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.models.content import Resource, Subject, Topic, TopicResource  # noqa: E402
from app.models.enums import Difficulty, NodeLevel, PriorityLevel, ResourceLevel, ResourceType  # noqa: E402

RESEARCH_DIR = Path(__file__).resolve().parent / "seed_data" / "research"

# The research agents' raw "subject" field sometimes embedded a long qualifier (e.g.
# "Deep Learning (Neural Networks / MLP) — NOTE: not an official standalone section...").
# We use a clean display name here and preserve that full caveat in the subject description
# instead of dropping it — Deep Learning and Data Science/Big Data are NOT official standalone
# GATE DA syllabus sections (see KNOWLEDGE_DEPENDENCY_MAP.md); is_official=False flags that
# in the UI so prep time isn't misallocated toward them.
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

_DIFFICULTY_KEYWORDS = [
    (Difficulty.VERY_HARD, ["very hard", "toughest"]),
    (Difficulty.HARD, ["hard", "difficult"]),
    (Difficulty.MEDIUM, ["moderate", "medium"]),
    (Difficulty.EASY, ["easy"]),
]

_PRIORITY_KEYWORDS = [
    (PriorityLevel.HIGH, ["high"]),
    (PriorityLevel.MEDIUM, ["medium"]),
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
    (ResourceType.ARTICLE, ResourceLevel.BEGINNER, "GO Classes", ["go classes"]),
]

# How much of the string counts as the "headline" naming the actual resource, as opposed to
# elaboration/caveats that often namedrop other unrelated platforms later in the same sentence
# (e.g. "Sheldon Ross's book ... (also recommended by GeeksforGeeks, GO Classes, ...)").
_HEADLINE_WINDOW = 120

_BOOK_PATTERN = re.compile(
    r"^[A-Z][A-Za-z.]+(?:\s[A-Z][A-Za-z.]+){0,4}(?:,\s[A-Z][A-Za-z.]+(?:\s[A-Z][A-Za-z.]+){0,3})*,\s*['\"]"
)


def classify_resource(text: str) -> tuple[ResourceType, ResourceLevel, str | None]:
    # Author-comma-'Title' is the book convention used throughout the research; check this
    # first since it's anchored at the string's start and far more reliable than a keyword
    # that might just be namedropped later in a long descriptive sentence.
    if _BOOK_PATTERN.match(text):
        return ResourceType.BOOK, ResourceLevel.INTERMEDIATE, None

    headline = text[:_HEADLINE_WINDOW].lower()
    for r_type, level, platform, keywords in _PLATFORM_RULES:
        if any(kw in headline for kw in keywords):
            return r_type, level, platform

    # Fall back to a full-text scan only if nothing matched in the headline window.
    lower = text.lower()
    for r_type, level, platform, keywords in _PLATFORM_RULES:
        if any(kw in lower for kw in keywords):
            return r_type, level, platform

    return ResourceType.ARTICLE, ResourceLevel.INTERMEDIATE, None


def extract_url(text: str) -> str | None:
    match = _URL_RE.search(text)
    if not match:
        return None
    domain_and_path = match.group(1)
    return f"https://{domain_and_path}"


def extract_title(text: str) -> str:
    for sep in [" — ", " – ", ": ", " (the ", ". "]:
        if sep in text:
            candidate = text.split(sep)[0].strip()
            if 8 <= len(candidate) <= 140:
                return candidate
    return text[:140].rsplit(" ", 1)[0] if len(text) > 140 else text


def infer_from_keywords(text: str, rules: list, default):
    lower = text.lower()
    for value, keywords in rules:
        if any(kw in lower for kw in keywords):
            return value
    return default


def load_subject_json(filename: str) -> dict:
    with open(RESEARCH_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def seed_subject(db: Session, order_index: int, entry: dict, data: dict) -> Subject:
    name = entry["name"]
    slug = slugify(name)[:120]
    raw_subject_field = data["subject"]

    weightage_text = data.get("weightagePercent", "")
    # Prefer an explicit "MIN-MAX%" range right next to the % sign over just grabbing the
    # first two numbers in the text — free-form research prose often mentions unrelated
    # numbers (years, question counts) right after the real range, e.g. General Aptitude's
    # "15% (fixed exactly - 10 questions/15 marks in 2024, 2025, and 2026...)" is a single
    # fixed value, not a "15-10%" range.
    range_match = re.search(r"(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)\s*%", weightage_text)
    if range_match:
        w_min, w_max = float(range_match.group(1)), float(range_match.group(2))
    else:
        single_match = re.search(r"(\d+(?:\.\d+)?)\s*%", weightage_text)
        w_min = w_max = float(single_match.group(1)) if single_match else None

    description_parts = []
    if not entry["is_official"] and raw_subject_field != name:
        # Preserve the researcher's original caveat verbatim rather than dropping it.
        description_parts.append(raw_subject_field)
    description_parts.append(data.get("pyqTrendByYear", ""))
    description = "\n\n".join(p for p in description_parts if p)[:4000] or None

    subject = Subject(
        slug=slug,
        name=name,
        description=description,
        weightage_min_percent=w_min,
        weightage_max_percent=w_max,
        difficulty=infer_from_keywords(data.get("difficulty", ""), _DIFFICULTY_KEYWORDS, Difficulty.MEDIUM),
        priority=infer_from_keywords(data.get("priorityForTopRank", ""), _PRIORITY_KEYWORDS, PriorityLevel.MEDIUM),
        order_index=order_index,
        is_official_section=entry["is_official"],
    )
    db.add(subject)
    db.flush()

    cheat_sheet_md = "\n".join(f"- {c}" for c in data.get("cheatSheet", []))
    mistakes_md = "\n".join(f"- {m}" for m in data.get("commonMistakes", []))

    subtopic_name_to_id: dict[str, int] = {}
    for i, sub in enumerate(data.get("subtopics", [])):
        topic = Topic(
            subject_id=subject.id,
            parent_id=None,
            slug=slugify(f"{slug}-{sub['name']}")[:160],
            name=sub["name"],
            level=NodeLevel.TOPIC,
            order_index=i,
            difficulty=_int_to_difficulty(sub.get("difficulty1to5")),
            importance_1to5=sub.get("importance1to5"),
            pyq_frequency=sub.get("pyqFrequency"),
            prerequisites_text=", ".join(sub.get("prerequisites") or []) or None,
            cheat_sheet_markdown=cheat_sheet_md or None,
            common_mistakes_markdown=mistakes_md or None,
        )
        db.add(topic)
        db.flush()
        subtopic_name_to_id[sub["name"]] = topic.id

    # Second pass: attach resources per subject to every topic in that subject
    # (subject-level resource lists aren't yet mapped 1:1 to a single subtopic).
    resource_ids: list[int] = []
    for raw in data.get("booksAndResources", []):
        r_type, level, platform = classify_resource(raw)
        resource = Resource(
            title=extract_title(raw),
            resource_type=r_type,
            level=level,
            url=extract_url(raw),
            platform=platform,
            description=raw,
            is_free=True,
        )
        db.add(resource)
        db.flush()
        resource_ids.append(resource.id)

    all_topic_ids = list(subtopic_name_to_id.values())
    for resource_id in resource_ids:
        for rank, topic_id in enumerate(all_topic_ids):
            db.add(TopicResource(topic_id=topic_id, resource_id=resource_id, relevance_rank=rank))

    return subject


def _int_to_difficulty(value: int | None) -> Difficulty | None:
    if value is None:
        return None
    return {1: Difficulty.EASY, 2: Difficulty.EASY, 3: Difficulty.MEDIUM, 4: Difficulty.HARD, 5: Difficulty.VERY_HARD}.get(
        value, Difficulty.MEDIUM
    )


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.query(Subject).count()
        if existing > 0:
            print(f"Database already has {existing} subjects — skipping seed (idempotent guard).")
            print("To reseed from scratch: drop and recreate the schema, then rerun this script.")
            return

        total_topics = 0
        total_resources = 0
        for i, entry in enumerate(SUBJECT_FILES):
            data = load_subject_json(entry["file"])
            subject = seed_subject(db, i, entry, data)
            n_topics = len(data.get("subtopics", []))
            n_resources = len(data.get("booksAndResources", []))
            total_topics += n_topics
            total_resources += n_resources
            official_tag = "" if entry["is_official"] else "  [not an official standalone section]"
            print(f"  seeded '{subject.name}': {n_topics} topics, {n_resources} resources{official_tag}")

        db.commit()
        print(f"\nDone. {len(SUBJECT_FILES)} subjects, {total_topics} topics, {total_resources} resources seeded.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
