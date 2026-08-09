from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from pilot_api.api.dependencies import get_session
from pilot_api.dto.schemas import AddResponseIntDto, ProblemDetailsDto
from pilot_api.service.crud_service import CrudService
from pilot_api.validation.rules import get_api_version


def create_service(
    session: Session,
    model_type: type[Any],
    dto_type: type[Any],
    pk_fields: list[str],
) -> CrudService:
    return CrudService(session=session, model_type=model_type, dto_type=dto_type, pk_fields=pk_fields)


def register_single_key_routes(
    *,
    prefix: str,
    tag: str,
    path_param_name: str,
    key_name: str,
    model_type: type[Any],
    dto_type: type[Any],
    id_cast: Callable[[Any], Any],
) -> APIRouter:
    router = APIRouter(tags=[tag])

    @router.get(f"/{prefix}/get-all", response_model=list[dto_type])
    def get_all(
        api_version: str | None = Depends(get_api_version),
        session: Session = Depends(get_session),
    ) -> list[dto_type]:
        _ = api_version
        return create_service(session, model_type, dto_type, [key_name]).get_all()

    @router.get(f"/{prefix}/get/{{{path_param_name}}}", response_model=dto_type)
    def get_one(
        item_id: str = Path(alias=path_param_name),
        api_version: str | None = Depends(get_api_version),
        session: Session = Depends(get_session),
    ) -> dto_type:
        _ = api_version
        keys = {key_name: id_cast(item_id)}
        return create_service(session, model_type, dto_type, [key_name]).get_one(keys)

    @router.post(f"/{prefix}/add", response_model=AddResponseIntDto)
    def add(
        payload: dto_type,
        api_version: str | None = Depends(get_api_version),
        session: Session = Depends(get_session),
    ) -> AddResponseIntDto:
        _ = api_version
        entity_id = create_service(session, model_type, dto_type, [key_name]).add(payload)
        if isinstance(entity_id, str):
            return AddResponseIntDto(id=0)
        return AddResponseIntDto(id=int(entity_id))

    @router.put(
        f"/{prefix}/update",
        status_code=204,
        response_model=None,
        responses={400: {"model": ProblemDetailsDto}},
    )
    def update(
        payload: dto_type,
        api_version: str | None = Depends(get_api_version),
        session: Session = Depends(get_session),
    ) -> None:
        _ = api_version
        create_service(session, model_type, dto_type, [key_name]).update(payload)

    @router.delete(
        f"/{prefix}/delete/{{{path_param_name}}}",
        status_code=204,
        responses={400: {"model": ProblemDetailsDto}},
    )
    def delete(
        item_id: str = Path(alias=path_param_name),
        api_version: str | None = Depends(get_api_version),
        session: Session = Depends(get_session),
    ) -> None:
        _ = api_version
        keys = {key_name: id_cast(item_id)}
        create_service(session, model_type, dto_type, [key_name]).delete(keys)

    return router
