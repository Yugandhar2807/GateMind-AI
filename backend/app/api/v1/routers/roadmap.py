import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.roadmap import ProgressUpdateRequest, SubjectNode, TopicProgressRead
from app.schemas.topic_detail import TopicDetail
from app.services.roadmap_service import RoadmapService, TopicNotFoundError

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.get("", response_model=list[SubjectNode])
def get_roadmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SubjectNode]:
    return RoadmapService(db).get_roadmap(current_user.id)


@router.get("/topics/{topic_id}", response_model=TopicDetail)
def get_topic_detail(
    topic_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TopicDetail:
    try:
        return RoadmapService(db).get_topic_detail(current_user.id, topic_id)
    except TopicNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found") from exc


@router.patch("/topics/{topic_id}/progress", response_model=TopicProgressRead)
def update_topic_progress(
    topic_id: uuid.UUID,
    payload: ProgressUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TopicProgressRead:
    try:
        return RoadmapService(db).update_progress(current_user, topic_id, payload)
    except TopicNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found") from exc
