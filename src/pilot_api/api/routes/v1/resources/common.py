from typing import Annotated, Any

from fastapi import APIRouter, Path, Query
from sqlalchemy.orm import Session

from pilot_api.api.dependencies import SessionDep
from pilot_api.dto.schemas import AddResponseIntDto, AddResponseStringDto
from pilot_api.service.crud_service import CrudService


def create_service(
    session: Session,
    model_type: type[Any],
    dto_type: type[Any],
    pk_fields: list[str],
) -> CrudService:
    return CrudService(
        session=session, model_type=model_type, dto_type=dto_type, pk_fields=pk_fields
    )


def register_single_key_routes(
    *,
    prefix: str,
    tag: str,
    path_param_name: str,
    key_name: str,
    model_type: type[Any],
    dto_type: type[Any],
    key_type: type[int] | type[str],
) -> APIRouter:
    router = APIRouter(tags=[tag])
    add_response_type = AddResponseStringDto if key_type is str else AddResponseIntDto
    # Typing the path param with key_type lets FastAPI reject a malformed id
    # (e.g. "abc" for an int key) as a 400 ProblemDetails instead of a 500.
    key_param = Annotated[key_type, Path(alias=path_param_name)]

    @router.get(f"/{prefix}/get-all", response_model=list[dto_type])
    def get_all(
        session: SessionDep,
        page: Annotated[int, Query(ge=0)] = 0,
        pageSize: Annotated[int, Query(ge=1)] = 20,
    ) -> list[dto_type]:
        return create_service(session, model_type, dto_type, [key_name]).get_all(page, pageSize)

    @router.get(f"/{prefix}/get/{{{path_param_name}}}", response_model=dto_type)
    def get_one(item_id: key_param, session: SessionDep) -> dto_type:
        keys = {key_name: item_id}
        return create_service(session, model_type, dto_type, [key_name]).get_one(keys)

    @router.post(f"/{prefix}/add", response_model=add_response_type, status_code=201)
    def add(payload: dto_type, session: SessionDep) -> AddResponseIntDto | AddResponseStringDto:
        entity_id = create_service(session, model_type, dto_type, [key_name]).add(payload)
        return add_response_type(id=entity_id)

    @router.put(f"/{prefix}/update", status_code=204, response_model=None)
    def update(payload: dto_type, session: SessionDep) -> None:
        create_service(session, model_type, dto_type, [key_name]).update(payload)

    @router.delete(f"/{prefix}/delete/{{{path_param_name}}}", status_code=204)
    def delete(item_id: key_param, session: SessionDep) -> None:
        keys = {key_name: item_id}
        create_service(session, model_type, dto_type, [key_name]).delete(keys)

    return router
