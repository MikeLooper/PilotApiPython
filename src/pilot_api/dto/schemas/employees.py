from pydantic import Field

from pilot_api.dto.schemas.base import DtoBase
from pilot_api.dto.schemas.fields import Int32Key, PastSqlDateTime, SqlDateTime


class EmployeesDto(DtoBase):
    address: str | None = Field(default=None, max_length=60)
    birthDate: PastSqlDateTime | None = None
    city: str | None = Field(default=None, max_length=15)
    country: str | None = Field(default=None, max_length=15)
    employeeId: Int32Key | None = None
    extension: str | None = Field(default=None, max_length=4)
    firstName: str = Field(min_length=1, max_length=10)
    hireDate: SqlDateTime | None = None
    homePhone: str | None = Field(default=None, max_length=24)
    lastName: str = Field(min_length=1, max_length=20)
    notes: str | None = None
    photo: str | None = Field(default=None, json_schema_extra={"format": "byte"})
    photoPath: str | None = Field(default=None, max_length=255)
    postalCode: str | None = Field(default=None, max_length=10)
    region: str | None = Field(default=None, max_length=15)
    reportsTo: Int32Key | None = None
    title: str | None = Field(default=None, max_length=30)
    titleOfCourtesy: str | None = Field(default=None, max_length=25)
