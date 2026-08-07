from pilot_api.api.routes.resources.common import register_single_key_routes
from pilot_api.dto.schemas import CategoriesDto
from pilot_api.model.entities import Category

router = register_single_key_routes(
    prefix="categories",
    tag="Categories",
    path_param_name="categoryId",
    key_name="categoryID",
    model_type=Category,
    dto_type=CategoriesDto,
    id_cast=int,
)
