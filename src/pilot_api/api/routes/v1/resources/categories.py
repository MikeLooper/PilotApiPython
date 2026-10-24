from pilot_api.api.routes.v1.resources.common import register_single_key_routes
from pilot_api.dto.schemas import CategoriesDto
from pilot_api.model.entities import Category

router = register_single_key_routes(
    prefix="categories",
    tag="Categories",
    path_param_name="categoryId",
    key_name="categoryId",
    model_type=Category,
    dto_type=CategoriesDto,
    key_type=int,
)
