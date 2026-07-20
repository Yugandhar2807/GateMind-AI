import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Note


class NoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: uuid.UUID, *, topic_id: uuid.UUID | None = None) -> list[Note]:
        stmt = (
            select(Note)
            .where(Note.user_id == user_id, Note.deleted_at.is_(None))
            .order_by(Note.updated_at.desc())
        )
        if topic_id is not None:
            stmt = stmt.where(Note.topic_id == topic_id)
        return list(self.db.scalars(stmt).all())

    def get_for_user(self, user_id: uuid.UUID, note_id: uuid.UUID) -> Note | None:
        return self.db.scalars(
            select(Note).where(Note.id == note_id, Note.user_id == user_id, Note.deleted_at.is_(None))
        ).first()
