from pilot_api.api.routes.v1.resources.common import register_single_key_routes
from pilot_api.dto.schemas import CustomersDto
from pilot_api.model.entities import Customer

router = register_single_key_routes(
    prefix="customers",
    tag="Customers",
    path_param_name="customerId",
    key_name="customerID",
    model_type=Customer,
    dto_type=CustomersDto,
    id_cast=str,
)
