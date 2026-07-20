"""
Ingest topic-SPECIFIC resources (researched via a dedicated workflow, see
scripts/seed_data/research/topic_specific_resources.json) for the highest-importance topics.

Unlike scripts/seed.py's subject-wide resource dump, these are matched to one exact topic
each and ranked above the generic subject-wide resources for that topic (negative
relevance_rank, so they sort first). Every URL here was actually found via WebSearch/WebFetch
by a research agent — never fabricated.

Usage:
    venv/Scripts/python.exe -m scripts.seed_topic_resources
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.models.content import Resource, Subject, Topic, TopicResource  # noqa: E402
from app.models.enums import ResourceLevel, ResourceType  # noqa: E402

DATA_FILE = Path(__file__).resolve().parent / "seed_data" / "research" / "topic_specific_resources.json"

TOPIC_RANK_START = -10  # sorts before the subject-wide dump's 0..N ranks


def main() -> None:
    db = SessionLocal()
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            entries = json.load(f)

        total_topics, total_resources, total_skipped_dupe, total_missing_topic = 0, 0, 0, 0

        for entry in entries:
            topic_name = entry.get("topic_name")
            subject_name = entry.get("subject")

            subject = db.scalars(select(Subject).where(Subject.name == subject_name)).first()
            if subject is None:
                print(f"  WARNING: subject '{subject_name}' not found, skipping '{topic_name}'")
                total_missing_topic += 1
                continue

            topic = db.scalars(
                select(Topic).where(Topic.subject_id == subject.id, Topic.name == topic_name)
            ).first()
            if topic is None:
                print(f"  WARNING: topic '{topic_name}' not found under '{subject_name}', skipping")
                total_missing_topic += 1
                continue

            resources = entry.get("resources", [])
            for rank, r in enumerate(resources):
                url = r.get("url")
                if not url:
                    continue

                existing = db.scalars(select(Resource).where(Resource.url == url)).first()
                if existing:
                    resource = existing
                    total_skipped_dupe += 1
                else:
                    try:
                        r_type = ResourceType(r["resource_type"])
                    except ValueError:
                        r_type = ResourceType.ARTICLE
                    try:
                        level = ResourceLevel(r["level"])
                    except ValueError:
                        level = ResourceLevel.INTERMEDIATE

                    resource = Resource(
                        title=r["title"],
                        resource_type=r_type,
                        level=level,
                        url=url,
                        platform=r.get("platform"),
                        instructor=r.get("instructor") or None,
                        description=r.get("description"),
                        is_free=r.get("is_free", True),
                    )
                    db.add(resource)
                    db.flush()
                    total_resources += 1

                already_linked = db.scalars(
                    select(TopicResource).where(
                        TopicResource.topic_id == topic.id, TopicResource.resource_id == resource.id
                    )
                ).first()
                if already_linked is None:
                    db.add(
                        TopicResource(
                            topic_id=topic.id,
                            resource_id=resource.id,
                            relevance_rank=TOPIC_RANK_START + rank,
                        )
                    )

            total_topics += 1
            print(f"  {topic_name[:70]}: {len(resources)} resource(s) linked")

        db.commit()
        print(
            f"\nDone. {total_topics} topics processed, {total_resources} new resources created, "
            f"{total_skipped_dupe} reused existing resources (already in DB), "
            f"{total_missing_topic} topics/subjects not found."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
