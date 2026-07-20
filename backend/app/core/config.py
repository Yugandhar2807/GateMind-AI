from datetime import date
from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ---- Database (Neon PostgreSQL) ----
    # A single connection string, e.g.
    #   postgresql://user:pass@ep-xxx-pooler.<region>.aws.neon.tech/neondb?sslmode=require
    DATABASE_URL: str

    # ---- Auth / JWT ----
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ---- OAuth (optional; wired in Phase 5+) ----
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None

    # ---- App ----
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # ---- Storage (Cloudinary) — optional until the upload features land ----
    CLOUDINARY_URL: str | None = None
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_MB: int = 10

    # ---- AI Mentor (local Ollama for dev; no hosted provider in prod yet) ----
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"

    # ---- Exam target (dashboard countdown / predictions) ----
    GATE_EXAM_DATE: date = date(2027, 2, 7)

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Normalise Neon's ``postgresql://`` URL to the SQLAlchemy psycopg (v3) driver."""
        url = self.DATABASE_URL
        if url.startswith("postgresql+"):
            return url
        if url.startswith("postgresql://"):
            return "postgresql+psycopg://" + url[len("postgresql://"):]
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://"):]
        return url

    @computed_field
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
