"""
Import curated, web-verified learning resources (scripts/seed_data/resources_*.json) into the rich
resources schema, linked to their topics. Idempotent per resource URL. Gold ranks above silver
above bronze within each topic's list (more-negative relevance_rank sorts first). Run after
scripts.seed_content.

Usage:
    venv/Scripts/python.exe -m scripts.import_resources
"""

import json
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.models.curriculum import Resource, Subject, Topic, TopicResource  # noqa: E402
from app.models.enums import ResourceCategory, ResourceLevel, ResourceRank, ResourceType  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent / "seed_data"
RANK_BASE = {"gold": -300, "silver": -200, "bronze": -100}


def _enum(cls, value, default):
    try:
        return cls(value)
    except (ValueError, KeyError, TypeError):
        return default


def main() -> None:
    db = SessionLocal()
    try:
        files = sorted(DATA_DIR.glob("resources_*.json"))
        if not files:
            print("No resources_*.json files found.")
            return

        created = reused = linked = missing = 0
        today = date.today()

        for fp in files:
            data = json.loads(fp.read_text(encoding="utf-8"))
            subject = db.scalars(select(Subject).where(Subject.name == data["subject"])).first()
            if subject is None:
                print(f"  WARN subject not found: {data['subject']}")
                continue

            for tp in data.get("topics", []):
                topic = db.scalars(
                    select(Topic).where(Topic.subject_id == subject.id, Topic.name == tp["topic_name"])
                ).first()
                if topic is None:
                    print(f"  WARN topic not found: {tp['topic_name']}")
                    missing += 1
                    continue

                for i, r in enumerate(tp.get("resources", [])):
                    url = r.get("url")
                    resource = (
                        db.scalars(select(Resource).where(Resource.url == url)).first() if url else None
                    )
                    if resource is None:
                        resource = Resource(
                            type=_enum(ResourceType, r.get("type"), ResourceType.ARTICLE),
                            title=r.get("title") or (url or "Untitled resource"),
                            url=url,
                            description=r.get("why_recommended"),
                            level=_enum(ResourceLevel, r.get("level"), ResourceLevel.INTERMEDIATE),
                            duration_minutes=r.get("duration_minutes"),
                            is_free=True,
                            category=_enum(ResourceCategory, r.get("category"), ResourceCategory.OTHER),
                            ranking=_enum(ResourceRank, r.get("ranking"), ResourceRank.SILVER),
                            instructor=r.get("instructor"),
                            channel=r.get("channel"),
                            organization=r.get("organization"),
                            provider=r.get("organization") or r.get("channel"),
                            language=r.get("language") or "English",
                            year=r.get("year"),
                            rating=r.get("rating"),
                            why_recommended=r.get("why_recommended"),
                            confidence_score=r.get("confidence_score"),
                            last_verified=today,
                            needs_review=bool(r.get("needs_review", False)),
                        )
                        db.add(resource)
                        db.flush()
                        created += 1
                    else:
                        reused += 1

                    rank = RANK_BASE.get(r.get("ranking") or "silver", -100) + i
                    existing_link = db.scalars(
                        select(TopicResource).where(
                            TopicResource.topic_id == topic.id, TopicResource.resource_id == resource.id
                        )
                    ).first()
                    if existing_link is None:
                        db.add(
                            TopicResource(
                                topic_id=topic.id,
                                resource_id=resource.id,
                                relevance_rank=rank,
                                is_topic_specific=True,
                            )
                        )
                        linked += 1

        db.commit()
        print(
            f"Imported from {len(files)} file(s): {created} new resources, {reused} reused, "
            f"{linked} topic links, {missing} topic mismatches."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
