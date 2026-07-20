from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, get_db
from app.models.enums import BookmarkType
from app.models.user import User
from app.schemas.bookmark import BookmarkRead, BookmarkToggleRequest, BookmarkToggleResponse
from app.services.bookmark_service import BookmarkService

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.get("", response_model=list[BookmarkRead])
def list_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[BookmarkRead]:
    return BookmarkService(db).list_for_user(current_user.id)


@router.get("/ids", response_model=list[int])
def bookmarked_ids(
    bookmark_type: BookmarkType,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[int]:
    return sorted(BookmarkService(db).bookmarked_target_ids(current_user.id, bookmark_type))


@router.post("/toggle", response_model=BookmarkToggleResponse)
def toggle_bookmark(
    payload: BookmarkToggleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BookmarkToggleResponse:
    return BookmarkService(db).toggle(current_user.id, payload)
