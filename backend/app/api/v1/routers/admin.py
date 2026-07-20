import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_admin, get_db
from app.models.curriculum import Resource, TopicResource
from app.schemas.admin import ResourceAdminRead, ResourceCreate, ResourceUpdate

# Every route here requires an admin (role=admin) via the router-level dependency.
router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])


@router.get("/resources", response_model=list[ResourceAdminRead])
def list_resources(
    needs_review: bool | None = None,
    is_approved: bool | None = None,
    is_obsolete: bool | None = None,
    limit: int = 200,
    db: Session = Depends(get_db),
) -> list[Resource]:
    stmt = select(Resource).order_by(Resource.created_at.desc())
    if needs_review is not None:
        stmt = stmt.where(Resource.needs_review == needs_review)
    if is_approved is not None:
        stmt = stmt.where(Resource.is_approved == is_approved)
    if is_obsolete is not None:
        stmt = stmt.where(Resource.is_obsolete == is_obsolete)
    return list(db.scalars(stmt.limit(min(limit, 1000))).all())


@router.post("/resources", response_model=ResourceAdminRead, status_code=status.HTTP_201_CREATED)
def create_resource(payload: ResourceCreate, db: Session = Depends(get_db)) -> Resource:
    data = payload.model_dump(exclude={"topic_id"})
    provider = data.get("organization") or data.get("channel")
    resource = Resource(**data, provider=provider, last_verified=date.today())
    db.add(resource)
    db.flush()
    if payload.topic_id is not None:
        db.add(
            TopicResource(
                topic_id=payload.topic_id, resource_id=resource.id, relevance_rank=0, is_topic_specific=True
            )
        )
    db.commit()
    db.refresh(resource)
    return resource


@router.patch("/resources/{resource_id}", response_model=ResourceAdminRead)
def update_resource(
    resource_id: uuid.UUID, payload: ResourceUpdate, db: Session = Depends(get_db)
) -> Resource:
    resource = db.get(Resource, resource_id)
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(resource, field, value)
    db.commit()
    db.refresh(resource)
    return resource


@router.post("/resources/{resource_id}/approve", response_model=ResourceAdminRead)
def approve_resource(resource_id: uuid.UUID, db: Session = Depends(get_db)) -> Resource:
    resource = db.get(Resource, resource_id)
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    resource.is_approved = True
    resource.needs_review = False
    db.commit()
    db.refresh(resource)
    return resource


@router.post("/resources/{resource_id}/obsolete", response_model=ResourceAdminRead)
def mark_obsolete(resource_id: uuid.UUID, db: Session = Depends(get_db)) -> Resource:
    resource = db.get(Resource, resource_id)
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    resource.is_obsolete = True
    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(resource_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    resource = db.get(Resource, resource_id)
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    db.delete(resource)
    db.commit()
