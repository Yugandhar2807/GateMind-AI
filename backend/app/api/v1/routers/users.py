import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, get_db
from app.core.config import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserProfileUpdate, UserRead

router = APIRouter(prefix="/users", tags=["users"])

_ALLOWED_PHOTO_TYPES = {"image/png", "image/jpeg", "image/webp"}


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead)
def update_me(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    repo = UserRepository(db)
    updated = repo.update(current_user, payload.model_dump(exclude_unset=True))
    return UserRead.model_validate(updated)


@router.post("/me/photo", response_model=UserRead)
async def upload_photo(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    if file.content_type not in _ALLOWED_PHOTO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image type: {file.content_type}",
        )

    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Photo exceeds {settings.MAX_UPLOAD_MB}MB limit",
        )

    upload_dir = Path(settings.UPLOAD_DIR) / "photos"
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename or "").suffix or ".jpg"
    filename = f"{uuid.uuid4().hex}{extension}"
    destination = upload_dir / filename
    destination.write_bytes(contents)

    repo = UserRepository(db)
    updated = repo.update(current_user, {"photo_url": f"/uploads/photos/{filename}"})
    return UserRead.model_validate(updated)
