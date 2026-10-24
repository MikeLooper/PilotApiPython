import pytest
from sqlalchemy.orm import Session

from pilot_api.exception.errors import ConflictError, NotFoundError
from pilot_api.model.entities import Category, OrderDetail
from pilot_api.repository.crud_repository import CrudRepository


def test_get_one_raises_not_found_when_entity_missing(db_session: Session) -> None:
    repository = CrudRepository(session=db_session, model=Category, pk_fields=["categoryId"])

    with pytest.raises(NotFoundError):
        repository.get_one({"categoryId": 999})


def test_add_raises_conflict_when_primary_key_exists(db_session: Session) -> None:
    repository = CrudRepository(session=db_session, model=Category, pk_fields=["categoryId"])

    repository.add(Category(categoryId=1, categoryName="Beverages", description=None, picture=None))
    db_session.commit()

    with pytest.raises(ConflictError):
        repository.add(
            Category(categoryId=1, categoryName="Duplicate", description=None, picture=None)
        )


def test_get_one_supports_composite_key_lookup(db_session: Session) -> None:
    repository = CrudRepository(
        session=db_session, model=OrderDetail, pk_fields=["orderId", "productId"]
    )

    repository.add(OrderDetail(orderId=1001, productId=7, unitPrice=12.5, quantity=2, discount=0.0))
    db_session.commit()

    entity = repository.get_one({"orderId": 1001, "productId": 7})

    assert entity.orderId == 1001
    assert entity.productId == 7
    assert entity.quantity == 2
