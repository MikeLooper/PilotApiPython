from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from pilot_api.api.dependencies import get_session
from pilot_api.dto.schemas import AboutResponseDto
from pilot_api.service.system_service import SystemService
from pilot_api.validation.rules import get_api_version

router = APIRouter(tags=["System"])


@router.get("/healthcheck", response_model=str)
def healthcheck(
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> str:
    _ = api_version
    return SystemService(session).healthcheck()


@router.get("/about", response_model=AboutResponseDto)
def about(
    show_details: bool = Query(default=False, alias="show-details"),
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> AboutResponseDto:
    _ = api_version
    return SystemService(session).about(show_details)
