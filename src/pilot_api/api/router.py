from fastapi import APIRouter

from pilot_api.api.routes.resources import router as resources_router
from pilot_api.api.routes.system import router as system_router

api_router = APIRouter()
api_router.include_router(resources_router)
api_router.include_router(system_router)
