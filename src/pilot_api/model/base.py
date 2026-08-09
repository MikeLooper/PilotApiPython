from sqlalchemy import Column, MetaData, Table
from sqlalchemy.orm import DeclarativeBase

from pilot_api.config.settings import get_settings

settings = get_settings()
schema_name = None if settings.resolved_database_url.startswith("sqlite") else settings.resolved_db_schema


def _normalize_identifier(name: str) -> str:
    if settings.db_backend.lower() == "postgresql":
        return name.replace(" ", "").lower()
    return name


class Base(DeclarativeBase):
    metadata = MetaData(schema=schema_name)

    @classmethod
    def __table_cls__(cls, *args, **kwargs):
        # Keep SQL Server naming untouched, but map to lowercase/no-space identifiers for PostgreSQL.
        if settings.db_backend.lower() != "postgresql":
            return Table(*args, **kwargs)

        mutable_args = list(args)
        mutable_args[0] = _normalize_identifier(mutable_args[0])

        for item in mutable_args[2:]:
            if isinstance(item, Column) and item.name:
                item.name = _normalize_identifier(item.name)

        return Table(*mutable_args, **kwargs)
