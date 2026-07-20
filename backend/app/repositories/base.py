from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Thin data-access layer. Services depend on repositories, never on the ORM directly."""

    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: Any) -> ModelType | None:
        return self.db.get(self.model, id)

    def list(self, *, offset: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def create(self, obj_in: dict[str, Any]) -> ModelType:
        obj = self.model(**obj_in)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelType, updates: dict[str, Any]) -> ModelType:
        for field, value in updates.items():
            setattr(obj, field, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.commit()
