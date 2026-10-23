from fastapi import APIRouter, Depends

from pilot_api.api.responses import RESOURCE_RESPONSES
from pilot_api.api.routes.v1.resources import router as resources_router
from pilot_api.security.security_helper import enforce_security
from pilot_api.validation.rules import get_api_version, get_correlation_id

API_VERSION = "1.0"

router = APIRouter(
    prefix=f"/v{API_VERSION.split('.')[0]}",
    dependencies=[Depends(get_api_version), Depends(get_correlation_id)],
    responses=RESOURCE_RESPONSES,
)
router.include_router(resources_router, dependencies=[Depends(enforce_security)])
