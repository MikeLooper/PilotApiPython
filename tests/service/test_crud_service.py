from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pilot_api.dto.schemas import CategoriesDto
from pilot_api.model.base import Base
from pilot_api.model.entities import Category
from pilot_api.service.crud_service import CrudService


def test_crud_service_add_get_update_delete_category() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    session = session_local()
    try:
        service = CrudService(session=session, model_type=Category, dto_type=CategoriesDto, pk_fields=["categoryID"])

        category = CategoriesDto(categoryID=8, categoryName="Seafood", description="Fresh", picture=None)
        inserted_id = service.add(category)
        assert inserted_id == 8

        fetched = service.get_one({"categoryID": 8})
        assert fetched.categoryName == "Seafood"

        updated = CategoriesDto(categoryID=8, categoryName="Seafood Updated", description="Fresh", picture=None)
        service.update(updated)
        fetched_after_update = service.get_one({"categoryID": 8})
        assert fetched_after_update.categoryName == "Seafood Updated"

        service.delete({"categoryID": 8})
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
