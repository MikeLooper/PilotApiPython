from decimal import Decimal

from sqlalchemy import Float, Numeric, cast
from sqlalchemy.types import TypeDecorator


class CrossDatabaseFloat(TypeDecorator):
    impl = Numeric(18, 4)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return Decimal(str(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return float(value)

    def column_expression(self, column):
        return cast(cast(column, Numeric), Float)