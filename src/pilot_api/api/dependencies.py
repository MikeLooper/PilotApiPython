from collections.abc import Generator

from sqlalchemy.orm import Session

from pilot_api.config.database import get_db_session


def get_session() -> Generator[Session, None, None]:
    yield from get_db_session()
