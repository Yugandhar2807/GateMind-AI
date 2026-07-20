from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bookmark import Bookmark
from app.models.content import Resource, Topic
from app.models.enums import BookmarkType
from app.models.flashcard import Flashcard
from app.models.note import Note
from app.schemas.bookmark import BookmarkRead, BookmarkToggleRequest, BookmarkToggleResponse


class BookmarkService:
    def __init__(self, db: Session):
        self.db = db

    def _resolve(self, bookmark_type: BookmarkType, target_id: int) -> tuple[str, str | None, str, bool]:
        """Returns (title, subtitle, link, is_missing) resolved live from the target's own table."""
        if bookmark_type == BookmarkType.RESOURCE:
            resource = self.db.get(Resource, target_id)
            if resource is None:
                return "(resource no longer exists)", None, "#", True
            return resource.title, resource.platform, resource.url or "#", False

        if bookmark_type == BookmarkType.TOPIC:
            topic = self.db.get(Topic, target_id)
            if topic is None:
                return "(topic no longer exists)", None, "#", True
            return topic.name, topic.subject.name, f"/roadmap/topics/{topic.id}", False

        if bookmark_type == BookmarkType.NOTE:
            note = self.db.get(Note, target_id)
            if note is None:
                return "(note no longer exists)", None, "#", True
            return note.title, "Note", "/notes", False

        if bookmark_type == BookmarkType.FLASHCARD:
            card = self.db.get(Flashcard, target_id)
            if card is None:
                return "(flashcard no longer exists)", None, "#", True
            return card.front_markdown[:100], card.topic.name, "/flashcards", False

        return f"({bookmark_type.value} bookmarking not yet supported)", None, "#", True

    def list_for_user(self, user_id: int) -> list[BookmarkRead]:
        stmt = select(Bookmark).where(Bookmark.user_id == user_id).order_by(Bookmark.created_at.desc())
        bookmarks = self.db.scalars(stmt).all()
        out = []
        for b in bookmarks:
            title, subtitle, link, is_missing = self._resolve(b.bookmark_type, b.target_id)
            out.append(
                BookmarkRead(
                    id=b.id,
                    bookmark_type=b.bookmark_type,
                    target_id=b.target_id,
                    notes=b.notes,
                    created_at=b.created_at,
                    title=title,
                    subtitle=subtitle,
                    link=link,
                    is_missing=is_missing,
                )
            )
        return out

    def bookmarked_target_ids(self, user_id: int, bookmark_type: BookmarkType) -> set[int]:
        stmt = select(Bookmark.target_id).where(Bookmark.user_id == user_id, Bookmark.bookmark_type == bookmark_type)
        return set(self.db.scalars(stmt).all())

    def toggle(self, user_id: int, payload: BookmarkToggleRequest) -> BookmarkToggleResponse:
        stmt = select(Bookmark).where(
            Bookmark.user_id == user_id,
            Bookmark.bookmark_type == payload.bookmark_type,
            Bookmark.target_id == payload.target_id,
        )
        existing = self.db.scalars(stmt).first()

        if existing:
            self.db.delete(existing)
            self.db.commit()
            return BookmarkToggleResponse(bookmarked=False, bookmark_id=None)

        bookmark = Bookmark(
            user_id=user_id,
            bookmark_type=payload.bookmark_type,
            target_id=payload.target_id,
            notes=payload.notes,
        )
        self.db.add(bookmark)
        self.db.commit()
        self.db.refresh(bookmark)
        return BookmarkToggleResponse(bookmarked=True, bookmark_id=bookmark.id)
