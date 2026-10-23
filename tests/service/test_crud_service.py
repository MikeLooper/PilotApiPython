from sqlalchemy.orm import Session

from pilot_api.dto.schemas import CategoriesDto
from pilot_api.model.entities import Category
from pilot_api.service.crud_service import CrudService


def test_crud_service_add_get_update_delete_category(db_session: Session) -> None:
    service = CrudService(
        session=db_session, model_type=Category, dto_type=CategoriesDto, pk_fields=["categoryId"]
    )

    category = CategoriesDto(
        categoryId=8, categoryName="Seafood", description="Fresh", picture=None
    )
    inserted_id = service.add(category)
    assert inserted_id == 8

    fetched = service.get_one({"categoryId": 8})
    assert fetched.categoryName == "Seafood"

    updated = CategoriesDto(
        categoryId=8, categoryName="Seafood Updated", description="Fresh", picture=None
    )
    service.update(updated)
    fetched_after_update = service.get_one({"categoryId": 8})
    assert fetched_after_update.categoryName == "Seafood Updated"

    service.delete({"categoryId": 8})
