from pilot_api.api.routes.v1.resources.common import register_single_key_routes
from pilot_api.dto.schemas import EmployeesDto
from pilot_api.model.entities import Employee

router = register_single_key_routes(
    prefix="employees",
    tag="Employees",
    path_param_name="employeeId",
    key_name="employeeID",
    model_type=Employee,
    dto_type=EmployeesDto,
    id_cast=int,
)
