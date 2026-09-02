from fastapi import APIRouter, Depends

from pilot_api.api.routes.v1.resources import router as resources_router
from pilot_api.security.security_helper import enforce_security

API_VERSION = "1.0"

router = APIRouter(prefix=f"/v{API_VERSION.split('.')[0]}")
router.include_router(resources_router, dependencies=[Depends(enforce_security)])
