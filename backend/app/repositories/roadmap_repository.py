from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.content import Resource, Subject, Topic, TopicResource
from app.models.progress import UserTopicProgress


class RoadmapRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_subjects_with_topics(self) -> list[Subject]:
        stmt = (
            select(Subject)
            .options(selectinload(Subject.topics))
            .order_by(Subject.order_index)
        )
        return list(self.db.scalars(stmt).unique().all())

    def progress_by_topic_id(self, user_id: int) -> dict[int, UserTopicProgress]:
        stmt = select(UserTopicProgress).where(UserTopicProgress.user_id == user_id)
        rows = self.db.scalars(stmt).all()
        return {row.topic_id: row for row in rows}

    def get_topic(self, topic_id: int) -> Topic | None:
        return self.db.get(Topic, topic_id)

    def get_topic_with_subject(self, topic_id: int) -> Topic | None:
        stmt = select(Topic).options(selectinload(Topic.subject)).where(Topic.id == topic_id)
        return self.db.scalars(stmt).first()

    def get_topic_resources(self, topic_id: int) -> list[Resource]:
        stmt = (
            select(Resource)
            .join(TopicResource, TopicResource.resource_id == Resource.id)
            .where(TopicResource.topic_id == topic_id)
            .order_by(TopicResource.relevance_rank)
        )
        return list(self.db.scalars(stmt).all())

    def get_or_create_progress(self, user_id: int, topic_id: int) -> UserTopicProgress:
        stmt = select(UserTopicProgress).where(
            UserTopicProgress.user_id == user_id, UserTopicProgress.topic_id == topic_id
        )
        progress = self.db.scalars(stmt).first()
        if progress is None:
            progress = UserTopicProgress(user_id=user_id, topic_id=topic_id)
            self.db.add(progress)
            self.db.flush()
        return progress
