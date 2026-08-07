import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pilot_api.exception.errors import ConflictError, NotFoundError
from pilot_api.model.base import Base
from pilot_api.model.entities import Category
from pilot_api.repository.crud_repository import CrudRepository


def test_category_repository_get_one_raises_not_found_when_entity_missing() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    session = session_local()
    try:
        repository = CrudRepository(session=session, model=Category, pk_fields=["categoryID"])

        with pytest.raises(NotFoundError):
            repository.get_one({"categoryID": 999})
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_category_repository_add_raises_conflict_when_primary_key_exists() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    session = session_local()
    try:
        repository = CrudRepository(session=session, model=Category, pk_fields=["categoryID"])

        repository.add(Category(categoryID=1, categoryName="Beverages", description=None, picture=None))
        session.commit()

        with pytest.raises(ConflictError):
            repository.add(Category(categoryID=1, categoryName="Duplicate", description=None, picture=None))
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
