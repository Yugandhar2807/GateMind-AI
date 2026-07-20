import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.curriculum import Resource, Subject, Topic, TopicResource
from app.models.progress import UserTopicProgress


class RoadmapRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_subjects(self) -> list[Subject]:
        return list(self.db.scalars(select(Subject).order_by(Subject.order_index)).all())

    def list_topics(self) -> list[Topic]:
        return list(self.db.scalars(select(Topic).order_by(Topic.subject_id, Topic.order_index)).all())

    def progress_by_topic_id(self, user_id: uuid.UUID) -> dict[uuid.UUID, UserTopicProgress]:
        rows = self.db.scalars(
            select(UserTopicProgress).where(UserTopicProgress.user_id == user_id)
        ).all()
        return {row.topic_id: row for row in rows}

    def get_topic(self, topic_id: uuid.UUID) -> Topic | None:
        return self.db.get(Topic, topic_id)

    def get_subject(self, subject_id: uuid.UUID) -> Subject | None:
        return self.db.get(Subject, subject_id)

    def get_topic_resources(self, topic_id: uuid.UUID) -> list[Resource]:
        stmt = (
            select(Resource)
            .join(TopicResource, TopicResource.resource_id == Resource.id)
            .where(TopicResource.topic_id == topic_id)
            .order_by(TopicResource.relevance_rank)
        )
        return list(self.db.scalars(stmt).all())

    def get_or_create_progress(self, user_id: uuid.UUID, topic_id: uuid.UUID) -> UserTopicProgress:
        stmt = select(UserTopicProgress).where(
            UserTopicProgress.user_id == user_id, UserTopicProgress.topic_id == topic_id
        )
        progress = self.db.scalars(stmt).first()
        if progress is None:
            progress = UserTopicProgress(user_id=user_id, topic_id=topic_id)
            self.db.add(progress)
            self.db.flush()
        return progress
