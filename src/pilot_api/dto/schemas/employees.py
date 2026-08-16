from datetime import datetime

from pydantic import field_validator

from pilot_api.dto.schemas.base import DtoBase, coerce_number


class EmployeesDto(DtoBase):
    address: str | None = None
    birthDate: datetime | None = None
    city: str | None = None
    country: str | None = None
    employeeID: int | None = None
    extension: str | None = None
    firstName: str | None
    hireDate: datetime | None = None
    homePhone: str | None = None
    lastName: str | None
    notes: str | None = None
    photo: str | None = None
    photoPath: str | None = None
    postalCode: str | None = None
    region: str | None = None
    reportsTo: int | None = None
    title: str | None = None
    titleOfCourtesy: str | None = None

    @field_validator("employeeID", "reportsTo", mode="before")
    @classmethod
    def validate_employee_numbers(cls, value: object) -> object:
        return coerce_number(value)
