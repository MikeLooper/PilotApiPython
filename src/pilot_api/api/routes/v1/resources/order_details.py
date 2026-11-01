from fastapi import APIRouter, Response

from pilot_api.api.dependencies import SessionDep
from pilot_api.api.responses import NO_CONTENT
from pilot_api.api.routes.v1.resources.common import (
    PageQuery,
    PageSizeQuery,
    create_service,
    ok_or_no_content,
)
from pilot_api.dto.schemas import AddResponseOrderDetailsDto, OrderDetailsDto
from pilot_api.dto.schemas.fields import Int32KeyParam
from pilot_api.model.entities import OrderDetail

router = APIRouter(tags=["OrderDetails"])

_PK_FIELDS = ["orderId", "productId"]


@router.get("/order-details/get-all", response_model=list[OrderDetailsDto], responses=NO_CONTENT)
def get_order_details_all(
    session: SessionDep,
    response: Response,
    page: PageQuery = 0,
    pageSize: PageSizeQuery = 20,
) -> list[OrderDetailsDto] | Response:
    service = create_service(session, OrderDetail, OrderDetailsDto, _PK_FIELDS)
    return ok_or_no_content(service.get_all(page, pageSize), response)


@router.get(
    "/order-details/get/product/{productId}/order/{orderId}",
    response_model=OrderDetailsDto,
    responses=NO_CONTENT,
)
def get_order_detail(
    productId: Int32KeyParam, orderId: Int32KeyParam, session: SessionDep, response: Response
) -> OrderDetailsDto | Response:
    keys = {"orderId": orderId, "productId": productId}
    return ok_or_no_content(
        create_service(session, OrderDetail, OrderDetailsDto, _PK_FIELDS).get_one(keys), response
    )


@router.post("/order-details/add", response_model=AddResponseOrderDetailsDto, status_code=201)
def add_order_detail(payload: OrderDetailsDto, session: SessionDep) -> AddResponseOrderDetailsDto:
    create_service(session, OrderDetail, OrderDetailsDto, _PK_FIELDS).add(payload)
    return AddResponseOrderDetailsDto(orderId=payload.orderId, productId=payload.productId)


@router.put("/order-details/update", status_code=204, response_model=None, responses=NO_CONTENT)
def update_order_detail(payload: OrderDetailsDto, session: SessionDep) -> None:
    create_service(session, OrderDetail, OrderDetailsDto, _PK_FIELDS).update(payload)


@router.delete(
    "/order-details/delete/product/{productId}/order/{orderId}",
    status_code=204,
    responses=NO_CONTENT,
)
def delete_order_detail(
    productId: Int32KeyParam, orderId: Int32KeyParam, session: SessionDep
) -> None:
    keys = {"orderId": orderId, "productId": productId}
    create_service(session, OrderDetail, OrderDetailsDto, _PK_FIELDS).delete(keys)
