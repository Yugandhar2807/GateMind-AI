import json
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.enums import ProgressStatus, ResourceLevel, RevisionStatus, SessionType
from app.models.progress import RevisionSchedule
from app.models.user import User
from app.repositories.roadmap_repository import RoadmapRepository
from app.schemas.roadmap import (
    DEFAULT_PROGRESS,
    ProgressUpdateRequest,
    SubjectNode,
    SubjectProgressSummary,
    TopicNode,
    TopicProgressRead,
)
from app.schemas.topic_detail import ResourceRead, TopicDetail
from app.services.activity_service import record_activity

REVISION_LADDER_DAYS = [1, 3, 7, 15, 30, 60, 90]


class TopicNotFoundError(Exception):
    pass


class RoadmapService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RoadmapRepository(db)

    def get_roadmap(self, user_id: uuid.UUID) -> list[SubjectNode]:
        subjects = self.repo.list_subjects()
        progress_map = self.repo.progress_by_topic_id(user_id)

        topics_by_subject: dict[uuid.UUID, list] = {}
        for topic in self.repo.list_topics():
            topics_by_subject.setdefault(topic.subject_id, []).append(topic)

        result: list[SubjectNode] = []
        for subject in subjects:
            nodes: list[TopicNode] = []
            counts = {s: 0 for s in ProgressStatus}
            completion_sum = 0.0

            for topic in topics_by_subject.get(subject.id, []):
                row = progress_map.get(topic.id)
                progress = TopicProgressRead.model_validate(row) if row else DEFAULT_PROGRESS
                counts[progress.status] += 1
                completion_sum += progress.completion_percent
                nodes.append(
                    TopicNode(
                        id=topic.id,
                        slug=topic.slug,
                        name=topic.name,
                        level=topic.level,
                        order_index=topic.order_index,
                        difficulty=topic.difficulty,
                        importance_1to5=topic.importance_1to5,
                        pyq_frequency=topic.pyq_frequency,
                        estimated_hours=topic.estimated_hours,
                        revision_frequency=topic.revision_frequency,
                        prerequisites_text=topic.prerequisites_text,
                        progress=progress,
                        children=[],
                    )
                )

            total = len(nodes)
            result.append(
                SubjectNode(
                    id=subject.id,
                    slug=subject.slug,
                    name=subject.name,
                    description=subject.description,
                    weightage_min_percent=subject.weightage_min_percent,
                    weightage_max_percent=subject.weightage_max_percent,
                    difficulty=subject.difficulty,
                    priority=subject.priority,
                    order_index=subject.order_index,
                    is_official_section=subject.is_official_section,
                    progress_summary=SubjectProgressSummary(
                        total=total,
                        completed=counts[ProgressStatus.COMPLETED],
                        in_progress=counts[ProgressStatus.IN_PROGRESS],
                        not_started=counts[ProgressStatus.NOT_STARTED],
                        needs_revision=counts[ProgressStatus.NEEDS_REVISION],
                        avg_completion_percent=round(completion_sum / total, 1) if total else 0.0,
                    ),
                    topics=nodes,
                )
            )
        return result

    def get_topic_detail(self, user_id: uuid.UUID, topic_id: uuid.UUID) -> TopicDetail:
        topic = self.repo.get_topic(topic_id)
        if topic is None:
            raise TopicNotFoundError(topic_id)
        subject = self.repo.get_subject(topic.subject_id)

        progress_row = self.repo.get_or_create_progress(user_id, topic_id)
        self.db.commit()
        resources = self.repo.get_topic_resources(topic_id)

        return TopicDetail(
            id=topic.id,
            slug=topic.slug,
            name=topic.name,
            level=topic.level,
            difficulty=topic.difficulty,
            importance_1to5=topic.importance_1to5,
            pyq_frequency=topic.pyq_frequency,
            estimated_hours=topic.estimated_hours,
            revision_frequency=topic.revision_frequency,
            prerequisites_text=topic.prerequisites_text,
            introduction=topic.introduction,
            theory_markdown=topic.theory_md,
            formulas_markdown=topic.formulas_md,
            real_world_applications=topic.real_world_applications_md,
            mind_map_json=json.dumps(topic.mind_map_json) if topic.mind_map_json else None,
            cheat_sheet_markdown=topic.cheat_sheet_md,
            common_mistakes_markdown=topic.common_mistakes_md,
            subject_id=topic.subject_id,
            subject_name=subject.name,
            subject_slug=subject.slug,
            progress=TopicProgressRead.model_validate(progress_row),
            resources=[
                ResourceRead(
                    id=r.id,
                    title=r.title,
                    resource_type=r.type,
                    level=r.level or ResourceLevel.INTERMEDIATE,
                    url=r.url,
                    platform=r.provider,
                    instructor=r.author,
                    description=r.description,
                    is_free=r.is_free,
                )
                for r in resources
            ],
        )

    def update_progress(
        self, user: User, topic_id: uuid.UUID, payload: ProgressUpdateRequest
    ) -> TopicProgressRead:
        topic = self.repo.get_topic(topic_id)
        if topic is None:
            raise TopicNotFoundError(topic_id)

        progress = self.repo.get_or_create_progress(user.id, topic_id)
        now = datetime.now(timezone.utc)
        was_completed = progress.status == ProgressStatus.COMPLETED

        if payload.status is not None:
            progress.status = payload.status
            if payload.status == ProgressStatus.COMPLETED and not was_completed:
                progress.completed_at = now
                progress.completion_percent = 100.0
                self._create_revision_ladder(user.id, topic_id, today=now.date())

        if payload.completion_percent is not None:
            progress.completion_percent = max(0.0, min(100.0, payload.completion_percent))

        minutes = payload.time_spent_minutes_delta or 0
        if minutes > 0:
            progress.time_spent_minutes += minutes
        progress.last_studied_at = now

        record_activity(self.db, user, minutes=minutes, session_type=SessionType.LEARNING, topic_id=topic_id)

        self.db.commit()
        self.db.refresh(progress)
        return TopicProgressRead.model_validate(progress)

    def _create_revision_ladder(self, user_id: uuid.UUID, topic_id: uuid.UUID, *, today: date) -> None:
        existing = {
            r.interval_day
            for r in self.db.query(RevisionSchedule)
            .filter(RevisionSchedule.user_id == user_id, RevisionSchedule.topic_id == topic_id)
            .all()
        }
        for days in REVISION_LADDER_DAYS:
            if days in existing:
                continue
            self.db.add(
                RevisionSchedule(
                    user_id=user_id,
                    topic_id=topic_id,
                    interval_day=days,
                    due_date=today + timedelta(days=days),
                    status=RevisionStatus.PENDING,
                )
            )
