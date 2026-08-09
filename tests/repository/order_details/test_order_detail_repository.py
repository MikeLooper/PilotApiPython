from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pilot_api.model.base import Base
from pilot_api.model.entities import OrderDetail
from pilot_api.repository.crud_repository import CrudRepository


def test_order_detail_repository_get_one_supports_composite_key_lookup() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    session = session_local()
    try:
        repository = CrudRepository(session=session, model=OrderDetail, pk_fields=["orderID", "productID"])

        repository.add(OrderDetail(orderID=1001, productID=7, unitPrice=12.5, quantity=2, discount=0.0))
        session.commit()

        entity = repository.get_one({"orderID": 1001, "productID": 7})

        assert entity.orderID == 1001
        assert entity.productID == 7
        assert entity.quantity == 2
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
