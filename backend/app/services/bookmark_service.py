import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Bookmark, Note
from app.models.content import Flashcard
from app.models.curriculum import Resource, Subject, Topic
from app.models.enums import BookmarkType
from app.schemas.bookmark import BookmarkRead, BookmarkToggleRequest, BookmarkToggleResponse


class BookmarkService:
    def __init__(self, db: Session):
        self.db = db

    def _resolve(self, btype: BookmarkType, target_id: uuid.UUID) -> tuple[str, str | None, str, bool]:
        """Returns (title, subtitle, link, is_missing) resolved live from the target's table."""
        if btype == BookmarkType.RESOURCE:
            r = self.db.get(Resource, target_id)
            if r is None:
                return "(resource no longer exists)", None, "#", True
            return r.title, r.provider, r.url or "#", False

        if btype == BookmarkType.TOPIC:
            t = self.db.get(Topic, target_id)
            if t is None:
                return "(topic no longer exists)", None, "#", True
            subject = self.db.get(Subject, t.subject_id)
            return t.name, subject.name if subject else None, f"/roadmap/topics/{t.id}", False

        if btype == BookmarkType.NOTE:
            n = self.db.get(Note, target_id)
            if n is None or n.deleted_at is not None:
                return "(note no longer exists)", None, "#", True
            return n.title, "Note", "/notes", False

        if btype == BookmarkType.FLASHCARD:
            c = self.db.get(Flashcard, target_id)
            if c is None:
                return "(flashcard no longer exists)", None, "#", True
            t = self.db.get(Topic, c.topic_id)
            return c.front_md[:100], (t.name if t else None), "/flashcards", False

        return f"({btype.value} bookmarking not yet supported)", None, "#", True

    def list_for_user(self, user_id: uuid.UUID) -> list[BookmarkRead]:
        rows = self.db.scalars(
            select(Bookmark)
            .where(Bookmark.user_id == user_id, Bookmark.deleted_at.is_(None))
            .order_by(Bookmark.created_at.desc())
        ).all()
        out = []
        for b in rows:
            title, subtitle, link, is_missing = self._resolve(b.target_type, b.target_id)
            out.append(
                BookmarkRead(
                    id=b.id,
                    bookmark_type=b.target_type,
                    target_id=b.target_id,
                    notes=b.note,
                    created_at=b.created_at,
                    title=title,
                    subtitle=subtitle,
                    link=link,
                    is_missing=is_missing,
                )
            )
        return out

    def bookmarked_target_ids(self, user_id: uuid.UUID, btype: BookmarkType) -> list[uuid.UUID]:
        return list(
            self.db.scalars(
                select(Bookmark.target_id).where(
                    Bookmark.user_id == user_id,
                    Bookmark.target_type == btype,
                    Bookmark.deleted_at.is_(None),
                )
            ).all()
        )

    def toggle(self, user_id: uuid.UUID, payload: BookmarkToggleRequest) -> BookmarkToggleResponse:
        existing = self.db.scalars(
            select(Bookmark).where(
                Bookmark.user_id == user_id,
                Bookmark.target_type == payload.bookmark_type,
                Bookmark.target_id == payload.target_id,
                Bookmark.deleted_at.is_(None),
            )
        ).first()
        if existing is not None:
            self.db.delete(existing)
            self.db.commit()
            return BookmarkToggleResponse(bookmarked=False, bookmark_id=None)

        bookmark = Bookmark(
            user_id=user_id,
            target_type=payload.bookmark_type,
            target_id=payload.target_id,
            note=payload.note,
        )
        self.db.add(bookmark)
        self.db.commit()
        self.db.refresh(bookmark)
        return BookmarkToggleResponse(bookmarked=True, bookmark_id=bookmark.id)
