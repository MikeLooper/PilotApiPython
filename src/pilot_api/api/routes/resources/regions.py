from pilot_api.api.routes.resources.common import register_single_key_routes
from pilot_api.dto.schemas import RegionsDto
from pilot_api.model.entities import Region

router = register_single_key_routes(
    prefix="regions",
    tag="Regions",
    path_param_name="regionId",
    key_name="regionID",
    model_type=Region,
    dto_type=RegionsDto,
    id_cast=int,
)
