from typing import Annotated

from fastapi import APIRouter, Query

from pilot_api.api.dependencies import SessionDep
from pilot_api.api.responses import SYSTEM_RESPONSES
from pilot_api.dto.schemas import AboutResponseDto
from pilot_api.service.system_service import SystemService

router = APIRouter(tags=["System"], responses=SYSTEM_RESPONSES)


@router.get("/healthcheck", response_model=str)
def healthcheck(session: SessionDep) -> str:
    return SystemService(session).healthcheck()


@router.get("/about", response_model=AboutResponseDto)
def about(
    session: SessionDep,
    show_details: Annotated[bool, Query(alias="show-details")] = False,
) -> AboutResponseDto:
    return SystemService(session).about(show_details)
