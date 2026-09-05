from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from pilot_api.api.dependencies import get_session
from pilot_api.api.routes.v1.resources.common import create_service
from pilot_api.dto.schemas import AddResponseIntDto, EmployeeTerritoriesDto, ProblemDetailsDto
from pilot_api.model.entities import EmployeeTerritory
from pilot_api.validation.rules import get_api_version

router = APIRouter(tags=["EmployeeTerritories"])


@router.get("/employee-territories/get-all", response_model=list[EmployeeTerritoriesDto])
def get_employee_territories_all(
    page: int = Query(default=0, ge=0),
    pageSize: int = Query(default=20, ge=1),
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> list[EmployeeTerritoriesDto]:
    _ = api_version
    return create_service(
        session,
        EmployeeTerritory,
        EmployeeTerritoriesDto,
        ["employeeID", "territoryID"],
    ).get_all(page, pageSize)


@router.get(
    "/employee-territories/get/employee/{employeeId}/territory/{territoryId}",
    response_model=EmployeeTerritoriesDto,
)
def get_employee_territory(
    employeeId: int,
    territoryId: str,
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> EmployeeTerritoriesDto:
    _ = api_version
    keys = {"employeeID": employeeId, "territoryID": territoryId}
    return create_service(
        session,
        EmployeeTerritory,
        EmployeeTerritoriesDto,
        ["employeeID", "territoryID"],
    ).get_one(keys)


@router.post("/employee-territories/add", response_model=AddResponseIntDto, status_code=201)
def add_employee_territory(
    payload: EmployeeTerritoriesDto,
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> AddResponseIntDto:
    _ = api_version
    create_service(
        session,
        EmployeeTerritory,
        EmployeeTerritoriesDto,
        ["employeeID", "territoryID"],
    ).add(payload)
    return AddResponseIntDto(id=payload.employeeID)


@router.put(
    "/employee-territories/update",
    status_code=204,
    response_model=None,
    responses={400: {"model": ProblemDetailsDto}},
)
def update_employee_territory(
    payload: EmployeeTerritoriesDto,
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> None:
    _ = api_version
    create_service(
        session,
        EmployeeTerritory,
        EmployeeTerritoriesDto,
        ["employeeID", "territoryID"],
    ).update(payload)


@router.delete(
    "/employee-territories/delete/employee/{employeeId}/territory/{territoryId}",
    status_code=204,
    responses={400: {"model": ProblemDetailsDto}},
)
def delete_employee_territory(
    employeeId: int,
    territoryId: str,
    api_version: str | None = Depends(get_api_version),
    session: Session = Depends(get_session),
) -> None:
    _ = api_version
    keys = {"employeeID": employeeId, "territoryID": territoryId}
    create_service(
        session,
        EmployeeTerritory,
        EmployeeTerritoriesDto,
        ["employeeID", "territoryID"],
    ).delete(keys)
