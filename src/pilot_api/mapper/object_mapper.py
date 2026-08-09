from typing import Any


def entity_to_dto(dto_type: type[Any], entity: Any) -> Any:
    return dto_type.model_validate(entity, from_attributes=True)


def dto_to_entity(entity_type: type[Any], dto: Any) -> Any:
    return entity_type(**dto.model_dump())
