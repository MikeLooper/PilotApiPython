from pilot_api.api.routes.v1.resources.common import register_single_key_routes
from pilot_api.dto.schemas import ProductsDto
from pilot_api.model.entities import Product

router = register_single_key_routes(
    prefix="products",
    tag="Products",
    path_param_name="productId",
    key_name="productID",
    model_type=Product,
    dto_type=ProductsDto,
    id_cast=int,
)
