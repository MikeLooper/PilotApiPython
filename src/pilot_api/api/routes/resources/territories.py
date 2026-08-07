from pilot_api.api.routes.resources.common import register_single_key_routes
from pilot_api.dto.schemas import TerritoriesDto
from pilot_api.model.entities import Territory

router = register_single_key_routes(
    prefix="territories",
    tag="Territories",
    path_param_name="territoryId",
    key_name="territoryID",
    model_type=Territory,
    dto_type=TerritoriesDto,
    id_cast=str,
)
