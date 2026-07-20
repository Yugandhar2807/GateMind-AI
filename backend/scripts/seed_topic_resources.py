"""
Ingest topic-SPECIFIC curated resources (scripts/seed_data/research/topic_specific_resources.json)
for the highest-importance topics — matched to one exact topic and ranked ABOVE the subject-wide
dump (negative relevance_rank, is_topic_specific=True). Every URL was found via real research,
never fabricated. Run AFTER scripts.seed_content. Idempotent per (topic, resource url).

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
from app.models.curriculum import Resource, Subject, Topic, TopicResource  # noqa: E402
from app.models.enums import ResourceLevel, ResourceType  # noqa: E402

DATA_FILE = Path(__file__).resolve().parent / "seed_data" / "research" / "topic_specific_resources.json"
RANK_START = -10  # sorts before the subject-wide dump's 0..N ranks


def main() -> None:
    db = SessionLocal()
    try:
        entries = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        topics_done = new_res = reused = missing = 0

        for entry in entries:
            subject = db.scalars(select(Subject).where(Subject.name == entry.get("subject"))).first()
            topic = None
            if subject is not None:
                topic = db.scalars(
                    select(Topic).where(Topic.subject_id == subject.id, Topic.name == entry.get("topic_name"))
                ).first()
            if topic is None:
                missing += 1
                print(f"  WARN topic not matched: {entry.get('subject')} / {entry.get('topic_name')}")
                continue

            for rank, r in enumerate(entry.get("resources", [])):
                url = r.get("url")
                if not url:
                    continue
                resource = db.scalars(select(Resource).where(Resource.url == url)).first()
                if resource is not None:
                    reused += 1
                else:
                    try:
                        r_type = ResourceType(r["resource_type"])
                    except (ValueError, KeyError):
                        r_type = ResourceType.ARTICLE
                    try:
                        level = ResourceLevel(r["level"])
                    except (ValueError, KeyError):
                        level = ResourceLevel.INTERMEDIATE
                    resource = Resource(
                        type=r_type,
                        title=r.get("title") or url,
                        url=url,
                        provider=r.get("platform"),
                        author=r.get("instructor") or None,
                        description=r.get("description"),
                        level=level,
                        is_free=r.get("is_free", True),
                    )
                    db.add(resource)
                    db.flush()
                    new_res += 1

                linked = db.scalars(
                    select(TopicResource).where(
                        TopicResource.topic_id == topic.id, TopicResource.resource_id == resource.id
                    )
                ).first()
                if linked is None:
                    db.add(
                        TopicResource(
                            topic_id=topic.id,
                            resource_id=resource.id,
                            relevance_rank=RANK_START + rank,
                            is_topic_specific=True,
                        )
                    )
            topics_done += 1

        db.commit()
        print(
            f"Topic-specific resources: {topics_done} topics matched, {new_res} new resources, "
            f"{reused} reused, {missing} topics not matched."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
