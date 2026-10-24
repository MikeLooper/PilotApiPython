from pilot_api.dto.schemas import CategoriesDto
from pilot_api.mapper.object_mapper import dto_to_entity, entity_to_dto
from pilot_api.model.entities import Category


def test_categories_entity_to_dto_maps_sqlalchemy_entity_to_pydantic_dto() -> None:
    entity = Category(categoryId=11, categoryName="Confections", description="Sweet", picture=None)

    dto = entity_to_dto(CategoriesDto, entity)

    assert dto.categoryId == 11
    assert dto.categoryName == "Confections"
    assert dto.description == "Sweet"


def test_categories_dto_to_entity_maps_pydantic_dto_to_sqlalchemy_entity() -> None:
    dto = CategoriesDto(categoryId=12, categoryName="Produce", description="Fresh", picture=None)

    entity = dto_to_entity(Category, dto)

    assert entity.categoryId == 12
    assert entity.categoryName == "Produce"
    assert entity.description == "Fresh"
