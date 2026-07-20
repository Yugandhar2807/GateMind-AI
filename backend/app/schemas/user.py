import uuid
from datetime import date, time

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import PreferredStudyTime, UserRole


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    target_score: int | None = Field(default=None, ge=0, le=100)
    target_air: int | None = Field(default=None, ge=1)
    daily_study_hours: float | None = Field(default=None, ge=0, le=24)
    preferred_study_time: PreferredStudyTime | None = None
    exam_date: date | None = None
    gym_time: time | None = None
    timezone: str | None = Field(default=None, max_length=64)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    photo_url: str | None
    target_score: int | None
    target_air: int | None
    daily_study_hours: float | None
    preferred_study_time: PreferredStudyTime | None
    exam_date: date | None
    gym_time: time | None
    timezone: str
    email_verified: bool
    current_streak_days: int
    longest_streak_days: int
    is_active: bool


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
