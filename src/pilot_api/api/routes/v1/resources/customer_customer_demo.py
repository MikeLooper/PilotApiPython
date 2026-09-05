from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from pilot_api.api.dependencies import get_session
from pilot_api.api.routes.v1.resources.common import create_service
from pilot_api.dto.schemas import AddResponseIntDto, CustomerCustomerDemoDto, ProblemDetailsDto
from pilot_api.model.entities import CustomerCustomerDemo
from pilot_api.validation.rules import get_api_version

router = APIRouter(tags=["CustomerCustomerDemo"])


@router.get("/customer-customer-demo/get-all", response_model=list[CustomerCustomerDemoDto])
def get_customer_customer_demo_all(
    page: int = Query(default=0, ge=0),
    pageSize: int = Query(default=20, ge=1),
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> list[CustomerCustomerDemoDto]:
    _ = api_version
    return create_service(
        session,
        CustomerCustomerDemo,
        CustomerCustomerDemoDto,
        ["customerID", "customerTypeID"],
    ).get_all(page, pageSize)


@router.get(
    "/customer-customer-demo/get/customer/{customerId}/type/{customerTypeId}",
    response_model=CustomerCustomerDemoDto,
)
def get_customer_customer_demo(
    customerId: str,
    customerTypeId: str,
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> CustomerCustomerDemoDto:
    _ = api_version
    keys = {"customerID": customerId, "customerTypeID": customerTypeId}
    return create_service(
        session,
        CustomerCustomerDemo,
        CustomerCustomerDemoDto,
        ["customerID", "customerTypeID"],
    ).get_one(keys)


@router.post("/customer-customer-demo/add", response_model=AddResponseIntDto, status_code=201)
def add_customer_customer_demo(
    payload: CustomerCustomerDemoDto,
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> AddResponseIntDto:
    _ = api_version
    create_service(
        session,
        CustomerCustomerDemo,
        CustomerCustomerDemoDto,
        ["customerID", "customerTypeID"],
    ).add(payload)
    return AddResponseIntDto(id=0)


@router.put(
    "/customer-customer-demo/update",
    status_code=204,
    response_model=None,
    responses={400: {"model": ProblemDetailsDto}},
)
def update_customer_customer_demo(
    payload: CustomerCustomerDemoDto,
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> None:
    _ = api_version
    create_service(
        session,
        CustomerCustomerDemo,
        CustomerCustomerDemoDto,
        ["customerID", "customerTypeID"],
    ).update(payload)


@router.delete(
    "/customer-customer-demo/delete/customer/{customerId}/type/{customerTypeId}",
    status_code=204,
    responses={400: {"model": ProblemDetailsDto}},
)
def delete_customer_customer_demo(
    customerId: str,
    customerTypeId: str,
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> None:
    _ = api_version
    keys = {"customerID": customerId, "customerTypeID": customerTypeId}
    create_service(
        session,
        CustomerCustomerDemo,
        CustomerCustomerDemoDto,
        ["customerID", "customerTypeID"],
    ).delete(keys)
