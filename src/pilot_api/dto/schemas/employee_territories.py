from pydantic import field_validator

from pilot_api.dto.schemas.base import DtoBase, coerce_number


class EmployeeTerritoriesDto(DtoBase):
    employeeID: int
    territoryID: str

    @field_validator("employeeID", mode="before")
    @classmethod
    def validate_employee_id(cls, value: object) -> object:
        return coerce_number(value)
