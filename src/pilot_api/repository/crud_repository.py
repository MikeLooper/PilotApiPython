from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from pilot_api.exception.errors import ConflictError, NotFoundError


class CrudRepository:
    def __init__(self, session: Session, model: type[Any], pk_fields: list[str]):
        self.session = session
        self.model = model
        self.pk_fields = pk_fields

    def get_all(self) -> Sequence[Any]:
        stmt = select(self.model)
        return self.session.execute(stmt).scalars().all()

    def get_one(self, keys: dict[str, Any]) -> Any:
        entity = self.session.get(self.model, tuple(keys[field] for field in self.pk_fields) if len(self.pk_fields) > 1 else keys[self.pk_fields[0]])
        if entity is None:
            raise NotFoundError(f"{self.model.__name__} not found.")
        return entity

    def add(self, entity: Any) -> Any:
        self.session.add(entity)
        try:
            self.session.flush()
        except IntegrityError as ex:
            raise ConflictError(f"{self.model.__name__} already exists.") from ex
        return entity

    def update(self, keys: dict[str, Any], data: dict[str, Any]) -> Any:
        entity = self.get_one(keys)
        for key, value in data.items():
            setattr(entity, key, value)
        self.session.flush()
        return entity

    def delete(self, keys: dict[str, Any]) -> None:
        entity = self.get_one(keys)
        self.session.delete(entity)
        self.session.flush()
