from pilot_api.api.routes.resources.common import register_single_key_routes
from pilot_api.dto.schemas import SuppliersDto
from pilot_api.model.entities import Supplier

router = register_single_key_routes(
    prefix="suppliers",
    tag="Suppliers",
    path_param_name="supplierId",
    key_name="supplierID",
    model_type=Supplier,
    dto_type=SuppliersDto,
    id_cast=int,
)
