from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from pilot_api.model.entities import Order, OrderDetail


def test_order_freight_is_cast_for_postgresql_reads() -> None:
    statement = select(Order)

    compiled = str(statement.compile(dialect=postgresql.dialect()))

    assert "CAST(CAST(" in compiled
    assert "freight AS NUMERIC) AS FLOAT" in compiled