from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from pilot_api.api.dependencies import get_session
from pilot_api.api.routes.resources.common import create_service
from pilot_api.dto.schemas import AddResponseIntDto, OrderDetailsDto, ProblemDetailsDto
from pilot_api.model.entities import OrderDetail
from pilot_api.validation.rules import get_api_version

router = APIRouter(tags=["OrderDetails"])


@router.get("/order-details/get-all", response_model=list[OrderDetailsDto])
def get_order_details_all(
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> list[OrderDetailsDto]:
    _ = api_version
    return create_service(session, OrderDetail, OrderDetailsDto, ["orderID", "productID"]).get_all()


@router.get("/order-details/get/product/{productId}/order/{orderId}", response_model=OrderDetailsDto)
def get_order_detail(
    productId: int,
    orderId: int,
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> OrderDetailsDto:
    _ = api_version
    keys = {"orderID": orderId, "productID": productId}
    return create_service(session, OrderDetail, OrderDetailsDto, ["orderID", "productID"]).get_one(keys)


@router.post("/order-details/add", response_model=AddResponseIntDto)
def add_order_detail(
    payload: OrderDetailsDto,
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> AddResponseIntDto:
    _ = api_version
    create_service(session, OrderDetail, OrderDetailsDto, ["orderID", "productID"]).add(payload)
    return AddResponseIntDto(id=payload.orderID)


@router.put(
    "/order-details/update",
    status_code=204,
    response_model=None,
    responses={400: {"model": ProblemDetailsDto}},
)
def update_order_detail(
    payload: OrderDetailsDto,
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> None:
    _ = api_version
    create_service(session, OrderDetail, OrderDetailsDto, ["orderID", "productID"]).update(payload)


@router.delete(
    "/order-details/delete/product/{productId}/order/{orderId}",
    status_code=204,
    responses={400: {"model": ProblemDetailsDto}},
)
def delete_order_detail(
    productId: int,
    orderId: int,
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> None:
    _ = api_version
    keys = {"orderID": orderId, "productID": productId}
    create_service(session, OrderDetail, OrderDetailsDto, ["orderID", "productID"]).delete(keys)
