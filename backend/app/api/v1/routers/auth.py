from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.core.security import TokenPayloadError, create_access_token, decode_token
from app.schemas.user import RefreshRequest, Token, UserLogin, UserRead, UserRegister
from app.services.auth_service import AuthService, EmailAlreadyRegisteredError, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> UserRead:
    service = AuthService(db)
    try:
        user = service.register(payload)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered") from exc
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    service = AuthService(db)
    try:
        user = service.authenticate(payload.email, payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password") from exc

    access_token, refresh_token = service.issue_tokens(user)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest) -> Token:
    try:
        token_payload = decode_token(payload.refresh_token, expected_type="refresh")
    except TokenPayloadError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    subject = token_payload["sub"]
    return Token(access_token=create_access_token(subject), refresh_token=payload.refresh_token)
