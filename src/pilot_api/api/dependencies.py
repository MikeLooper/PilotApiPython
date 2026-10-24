from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from pilot_api.config.database import get_db_session
from pilot_api.config.request_settings import RequestSettings


def get_session() -> Generator[Session, None, None]:
    yield from get_db_session()


SessionDep = Annotated[Session, Depends(get_session)]


def get_request_settings(request: Request) -> RequestSettings:
    return request.state.request_settings


RequestSettingsDep = Annotated[RequestSettings, Depends(get_request_settings)]
