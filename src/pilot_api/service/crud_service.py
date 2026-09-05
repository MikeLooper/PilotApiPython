from typing import Any

from sqlalchemy.orm import Session

from pilot_api.mapper.object_mapper import dto_to_entity, entity_to_dto
from pilot_api.repository.crud_repository import CrudRepository


class CrudService:
    def __init__(
        self,
        session: Session,
        model_type: type[Any],
        dto_type: type[Any],
        pk_fields: list[str],
    ):
        self.session = session
        self.model_type = model_type
        self.dto_type = dto_type
        self.repository = CrudRepository(session=session, model=model_type, pk_fields=pk_fields)
        self.pk_fields = pk_fields

    def get_all(self, page: int = 0, page_size: int = 20) -> list[Any]:
        return [entity_to_dto(self.dto_type, entity) for entity in self.repository.get_all(page, page_size)]

    def get_one(self, keys: dict[str, Any]) -> Any:
        entity = self.repository.get_one(keys)
        return entity_to_dto(self.dto_type, entity)

    def add(self, dto: Any) -> int | str:
        entity = dto_to_entity(self.model_type, dto)
        self.repository.add(entity)
        self.session.commit()
        if len(self.pk_fields) == 1:
            return getattr(entity, self.pk_fields[0])
        return 0

    def update(self, dto: Any) -> None:
        keys = {key: getattr(dto, key) for key in self.pk_fields}
        self.repository.update(keys, dto.model_dump())
        self.session.commit()

    def delete(self, keys: dict[str, Any]) -> None:
        self.repository.delete(keys)
        self.session.commit()
