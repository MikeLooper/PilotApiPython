from pilot_api.api.routes.v1.resources.common import register_single_key_routes
from pilot_api.dto.schemas import ShippersDto
from pilot_api.model.entities import Shipper

router = register_single_key_routes(
    prefix="shippers",
    tag="Shippers",
    path_param_name="shipperId",
    key_name="shipperID",
    model_type=Shipper,
    dto_type=ShippersDto,
    id_cast=int,
)
