from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.enums import ProgressStatus, RevisionInterval, RevisionStatus, SessionType
from app.models.revision import RevisionSchedule
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


class TopicNotFoundError(Exception):
    pass


REVISION_LADDER_DAYS = [interval.value for interval in RevisionInterval]


class RoadmapService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RoadmapRepository(db)

    def get_roadmap(self, user_id: int) -> list[SubjectNode]:
        subjects = self.repo.list_subjects_with_topics()
        progress_map = self.repo.progress_by_topic_id(user_id)

        result: list[SubjectNode] = []
        for subject in subjects:
            topic_nodes: list[TopicNode] = []
            status_counts = {s: 0 for s in ProgressStatus}
            completion_sum = 0.0

            for topic in sorted(subject.topics, key=lambda t: t.order_index):
                progress_row = progress_map.get(topic.id)
                progress = (
                    TopicProgressRead.model_validate(progress_row) if progress_row else DEFAULT_PROGRESS
                )
                status_counts[progress.status] += 1
                completion_sum += progress.completion_percent

                topic_nodes.append(
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

            total = len(topic_nodes)
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
                        completed=status_counts[ProgressStatus.COMPLETED],
                        in_progress=status_counts[ProgressStatus.IN_PROGRESS],
                        not_started=status_counts[ProgressStatus.NOT_STARTED],
                        needs_revision=status_counts[ProgressStatus.NEEDS_REVISION],
                        avg_completion_percent=round(completion_sum / total, 1) if total else 0.0,
                    ),
                    topics=topic_nodes,
                )
            )

        return result

    def get_topic_detail(self, user_id: int, topic_id: int) -> TopicDetail:
        topic = self.repo.get_topic_with_subject(topic_id)
        if topic is None:
            raise TopicNotFoundError(topic_id)

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
            theory_markdown=topic.theory_markdown,
            formulas_markdown=topic.formulas_markdown,
            real_world_applications=topic.real_world_applications,
            mind_map_json=topic.mind_map_json,
            cheat_sheet_markdown=topic.cheat_sheet_markdown,
            common_mistakes_markdown=topic.common_mistakes_markdown,
            subject_id=topic.subject_id,
            subject_name=topic.subject.name,
            subject_slug=topic.subject.slug,
            progress=TopicProgressRead.model_validate(progress_row),
            resources=[ResourceRead.model_validate(r) for r in resources],
        )

    def update_progress(self, user: User, topic_id: int, payload: ProgressUpdateRequest) -> TopicProgressRead:
        topic = self.repo.get_topic(topic_id)
        if topic is None:
            raise TopicNotFoundError(topic_id)

        progress = self.repo.get_or_create_progress(user.id, topic_id)
        now = datetime.utcnow()
        was_completed = progress.status == ProgressStatus.COMPLETED

        if payload.status is not None:
            progress.status = payload.status
            if progress.started_at is None and payload.status != ProgressStatus.NOT_STARTED:
                progress.started_at = now
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

    def _create_revision_ladder(self, user_id: int, topic_id: int, *, today: date) -> None:
        existing = {
            row.interval_stage
            for row in self.db.query(RevisionSchedule)
            .filter(RevisionSchedule.user_id == user_id, RevisionSchedule.topic_id == topic_id)
            .all()
        }
        for days in REVISION_LADDER_DAYS:
            stage = RevisionInterval(days)
            if stage in existing:
                continue
            self.db.add(
                RevisionSchedule(
                    user_id=user_id,
                    topic_id=topic_id,
                    interval_stage=stage,
                    scheduled_date=today + timedelta(days=days),
                    status=RevisionStatus.PENDING,
                )
            )
