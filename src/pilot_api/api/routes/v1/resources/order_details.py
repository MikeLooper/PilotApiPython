from typing import Annotated

from fastapi import APIRouter, Query

from pilot_api.api.dependencies import SessionDep
from pilot_api.api.routes.v1.resources.common import create_service
from pilot_api.dto.schemas import AddResponseOrderDetailsDto, OrderDetailsDto
from pilot_api.model.entities import OrderDetail

router = APIRouter(tags=["OrderDetails"])

_PK_FIELDS = ["orderId", "productId"]


@router.get("/order-details/get-all", response_model=list[OrderDetailsDto])
def get_order_details_all(
    session: SessionDep,
    page: Annotated[int, Query(ge=0)] = 0,
    pageSize: Annotated[int, Query(ge=1)] = 20,
) -> list[OrderDetailsDto]:
    return create_service(session, OrderDetail, OrderDetailsDto, _PK_FIELDS).get_all(page, pageSize)


@router.get(
    "/order-details/get/product/{productId}/order/{orderId}", response_model=OrderDetailsDto
)
def get_order_detail(productId: int, orderId: int, session: SessionDep) -> OrderDetailsDto:
    keys = {"orderId": orderId, "productId": productId}
    return create_service(session, OrderDetail, OrderDetailsDto, _PK_FIELDS).get_one(keys)


@router.post("/order-details/add", response_model=AddResponseOrderDetailsDto, status_code=201)
def add_order_detail(payload: OrderDetailsDto, session: SessionDep) -> AddResponseOrderDetailsDto:
    create_service(session, OrderDetail, OrderDetailsDto, _PK_FIELDS).add(payload)
    return AddResponseOrderDetailsDto(orderId=payload.orderId, productId=payload.productId)


@router.put("/order-details/update", status_code=204, response_model=None)
def update_order_detail(payload: OrderDetailsDto, session: SessionDep) -> None:
    create_service(session, OrderDetail, OrderDetailsDto, _PK_FIELDS).update(payload)


@router.delete("/order-details/delete/product/{productId}/order/{orderId}", status_code=204)
def delete_order_detail(productId: int, orderId: int, session: SessionDep) -> None:
    keys = {"orderId": orderId, "productId": productId}
    create_service(session, OrderDetail, OrderDetailsDto, _PK_FIELDS).delete(keys)
