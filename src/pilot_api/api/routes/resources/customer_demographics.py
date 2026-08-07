from pilot_api.api.routes.resources.common import register_single_key_routes
from pilot_api.dto.schemas import CustomerDemographicsDto
from pilot_api.model.entities import CustomerDemographic

router = register_single_key_routes(
    prefix="customer-demographics",
    tag="CustomerDemographics",
    path_param_name="customerTypeId",
    key_name="customerTypeID",
    model_type=CustomerDemographic,
    dto_type=CustomerDemographicsDto,
    id_cast=str,
)
