from collections.abc import Callable
from typing import Annotated, Any

from fastapi import APIRouter, Path, Query, Response
from pydantic import AfterValidator
from sqlalchemy.orm import Session

from pilot_api.api.dependencies import SessionDep
from pilot_api.api.responses import NO_CONTENT
from pilot_api.dto.schemas import AddResponseIntDto, AddResponseStringDto
from pilot_api.dto.schemas.fields import Int32KeyParam, Int32Param, StringKey
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


def ok_or_no_content(result: Any, response: Response) -> Any:
    # The definition answers a Get that finds nothing with a 204, not an empty 200 or a 404.
    # FastAPI ignores the injected response once a Response is returned, so its headers (e.g.
    # the security Warning) are carried over.
    return result if result else Response(status_code=204, headers=dict(response.headers))


def _at_least(minimum: int) -> Callable[[int], int]:
    # Validated here rather than with Query(ge=...) so the bound stays out of the OpenAPI
    # document, which (like the shared definition) declares no minimum.
    def check(value: int) -> int:
        if value < minimum:
            raise ValueError(f"Input should be greater than or equal to {minimum}")
        return value

    return check


PageQuery = Annotated[Int32Param, Query(), AfterValidator(_at_least(0))]
PageSizeQuery = Annotated[Int32Param, Query(), AfterValidator(_at_least(1))]


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
    # Typing the path param with the constrained key lets FastAPI reject a malformed id
    # (e.g. "abc" or 0 for an int key) as a 400 ProblemDetails instead of a 500.
    key_param = Annotated[
        Int32KeyParam if key_type is int else StringKey, Path(alias=path_param_name)
    ]

    @router.get(f"/{prefix}/get-all", response_model=list[dto_type], responses=NO_CONTENT)
    def get_all(
        session: SessionDep,
        response: Response,
        page: PageQuery = 0,
        pageSize: PageSizeQuery = 20,
    ) -> list[dto_type] | Response:
        service = create_service(session, model_type, dto_type, [key_name])
        return ok_or_no_content(service.get_all(page, pageSize), response)

    @router.get(
        f"/{prefix}/get/{{{path_param_name}}}", response_model=dto_type, responses=NO_CONTENT
    )
    def get_one(item_id: key_param, session: SessionDep, response: Response) -> dto_type | Response:
        keys = {key_name: item_id}
        return ok_or_no_content(
            create_service(session, model_type, dto_type, [key_name]).get_one(keys), response
        )

    @router.post(f"/{prefix}/add", response_model=add_response_type, status_code=201)
    def add(payload: dto_type, session: SessionDep) -> AddResponseIntDto | AddResponseStringDto:
        entity_id = create_service(session, model_type, dto_type, [key_name]).add(payload)
        return add_response_type(id=entity_id)

    @router.put(f"/{prefix}/update", status_code=204, response_model=None, responses=NO_CONTENT)
    def update(payload: dto_type, session: SessionDep) -> None:
        create_service(session, model_type, dto_type, [key_name]).update(payload)

    @router.delete(f"/{prefix}/delete/{{{path_param_name}}}", status_code=204, responses=NO_CONTENT)
    def delete(item_id: key_param, session: SessionDep) -> None:
        keys = {key_name: item_id}
        create_service(session, model_type, dto_type, [key_name]).delete(keys)

    return router
