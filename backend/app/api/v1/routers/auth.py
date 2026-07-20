from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.schemas.user import RefreshRequest, Token, UserLogin, UserRead, UserRegister
from app.services.auth_service import (
    AuthService,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> UserRead:
    try:
        user = AuthService(db).register(payload)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered") from exc
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)) -> Token:
    service = AuthService(db)
    try:
        user = service.authenticate(payload.email, payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        ) from exc

    access, refresh = service.issue_tokens(user, request.headers.get("user-agent"))
    return Token(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)) -> Token:
    try:
        access, new_refresh = AuthService(db).rotate_refresh(
            payload.refresh_token, request.headers.get("user-agent")
        )
    except InvalidRefreshTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
        ) from exc
    return Token(access_token=access, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)) -> Response:
    AuthService(db).logout(payload.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
