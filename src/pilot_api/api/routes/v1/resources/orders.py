from pilot_api.api.routes.v1.resources.common import register_single_key_routes
from pilot_api.dto.schemas import OrdersDto
from pilot_api.model.entities import Order

router = register_single_key_routes(
    prefix="orders",
    tag="Orders",
    path_param_name="orderId",
    key_name="orderID",
    model_type=Order,
    dto_type=OrdersDto,
    id_cast=int,
)
