from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from pilot_api.config.settings import get_settings

settings = get_settings()
schema_name = None if settings.resolved_database_url.startswith("sqlite") else settings.db_schema


class Base(DeclarativeBase):
    metadata = MetaData(schema=schema_name)
