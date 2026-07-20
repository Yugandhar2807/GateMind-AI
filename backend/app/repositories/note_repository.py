from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.note import Note


class NoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: int, *, topic_id: int | None = None) -> list[Note]:
        stmt = select(Note).where(Note.user_id == user_id).order_by(Note.updated_at.desc())
        if topic_id is not None:
            stmt = stmt.where(Note.topic_id == topic_id)
        return list(self.db.scalars(stmt).all())

    def get_for_user(self, user_id: int, note_id: int) -> Note | None:
        stmt = select(Note).where(Note.id == note_id, Note.user_id == user_id)
        return self.db.scalars(stmt).first()
