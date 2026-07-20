import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    TokenPayloadError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.enums import AuthProvider
from app.models.user import AuthIdentity, RefreshToken, User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegister


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    # ---- Registration & password login ----
    def register(self, payload: UserRegister) -> User:
        if self.users.get_by_email(payload.email):
            raise EmailAlreadyRegisteredError(payload.email)
        return self.users.create(
            {
                "email": payload.email,
                "hashed_password": hash_password(payload.password),
                "full_name": payload.full_name,
            }
        )

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if user is None or not user.hashed_password or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InvalidCredentialsError()
        return user

    # ---- Token issuance with refresh-token rotation ----
    def issue_tokens(self, user: User, user_agent: str | None = None) -> tuple[str, str]:
        subject = str(user.id)
        access = create_access_token(subject)
        refresh = create_refresh_token(subject)
        self._persist_refresh(user.id, refresh, user_agent)
        return access, refresh

    def _persist_refresh(self, user_id: uuid.UUID, refresh: str, user_agent: str | None) -> None:
        self.db.add(
            RefreshToken(
                user_id=user_id,
                token_hash=hash_token(refresh),
                expires_at=datetime.now(timezone.utc)
                + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
                user_agent=user_agent[:255] if user_agent else None,
            )
        )
        self.db.commit()

    def rotate_refresh(self, refresh_token: str, user_agent: str | None = None) -> tuple[str, str]:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except TokenPayloadError as exc:
            raise InvalidRefreshTokenError() from exc

        row = self.db.scalars(
            select(RefreshToken).where(RefreshToken.token_hash == hash_token(refresh_token))
        ).first()
        now = datetime.now(timezone.utc)
        # Reject unknown, already-rotated (reuse), or expired tokens.
        if row is None or row.revoked_at is not None or row.expires_at <= now:
            raise InvalidRefreshTokenError()

        row.revoked_at = now  # single-use: rotating invalidates the presented token
        user_id = uuid.UUID(str(payload["sub"]))
        access = create_access_token(str(user_id))
        new_refresh = create_refresh_token(str(user_id))
        self._persist_refresh(user_id, new_refresh, user_agent)  # commits row.revoked_at too
        return access, new_refresh

    def logout(self, refresh_token: str) -> None:
        row = self.db.scalars(
            select(RefreshToken).where(RefreshToken.token_hash == hash_token(refresh_token))
        ).first()
        if row is not None and row.revoked_at is None:
            row.revoked_at = datetime.now(timezone.utc)
            self.db.commit()

    # ---- OAuth scaffold (Google/GitHub callbacks call this in a later phase) ----
    def get_or_create_oauth_user(
        self, provider: AuthProvider, provider_user_id: str, email: str, full_name: str
    ) -> User:
        identity = self.db.scalars(
            select(AuthIdentity).where(
                AuthIdentity.provider == provider,
                AuthIdentity.provider_user_id == provider_user_id,
            )
        ).first()
        if identity is not None:
            return self.db.get(User, identity.user_id)

        user = self.users.get_by_email(email)
        if user is None:
            user = self.users.create(
                {"email": email, "full_name": full_name, "hashed_password": None, "email_verified": True}
            )
        self.db.add(
            AuthIdentity(user_id=user.id, provider=provider, provider_user_id=provider_user_id, email=email)
        )
        self.db.commit()
        return user
