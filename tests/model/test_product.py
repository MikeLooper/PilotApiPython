from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from pilot_api.model.entities import Product


def test_product_unit_price_is_cast_for_postgresql_reads() -> None:
    statement = select(Product)

    compiled = str(statement.compile(dialect=postgresql.dialect()))

    assert "CAST(CAST(" in compiled
    assert "unitprice AS NUMERIC) AS FLOAT" in compiled