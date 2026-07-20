import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, get_db
from app.models.activity import Note
from app.models.user import User
from app.repositories.note_repository import NoteRepository
from app.schemas.note import NoteCreate, NoteRead, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


def _read(n: Note) -> NoteRead:
    return NoteRead(
        id=n.id,
        title=n.title,
        content_markdown=n.content_md,
        topic_id=n.topic_id,
        created_at=n.created_at,
        updated_at=n.updated_at,
    )


@router.get("", response_model=list[NoteRead])
def list_notes(
    topic_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NoteRead]:
    return [_read(n) for n in NoteRepository(db).list_for_user(current_user.id, topic_id=topic_id)]


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NoteRead:
    note = Note(
        user_id=current_user.id,
        title=payload.title,
        content_md=payload.content_markdown,
        topic_id=payload.topic_id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return _read(note)


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(
    note_id: uuid.UUID,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NoteRead:
    note = NoteRepository(db).get_for_user(current_user.id, note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    data = payload.model_dump(exclude_unset=True)
    if "content_markdown" in data:
        note.content_md = data.pop("content_markdown")
    for field, value in data.items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return _read(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    note = NoteRepository(db).get_for_user(current_user.id, note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    note.deleted_at = datetime.now(timezone.utc)  # soft delete
    db.commit()
