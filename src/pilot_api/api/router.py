from fastapi import APIRouter

from pilot_api.api.routes.system import router as system_router
from pilot_api.api.routes.v1 import router as v1_router

api_router = APIRouter()
api_router.include_router(v1_router)
api_router.include_router(system_router)
