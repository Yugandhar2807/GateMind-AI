"""Single import point for Alembic autogenerate: Base.metadata + every model."""

from app.db.base_class import Base  # noqa: F401
import app.models  # noqa: F401  (imports all model modules, registering them on Base.metadata)
