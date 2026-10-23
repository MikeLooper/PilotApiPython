from fastapi import APIRouter

from pilot_api.api.routes.v1.resources.categories import router as categories_router
from pilot_api.api.routes.v1.resources.customers import router as customers_router
from pilot_api.api.routes.v1.resources.employees import router as employees_router
from pilot_api.api.routes.v1.resources.order_details import router as order_details_router
from pilot_api.api.routes.v1.resources.orders import router as orders_router
from pilot_api.api.routes.v1.resources.products import router as products_router
from pilot_api.api.routes.v1.resources.shippers import router as shippers_router
from pilot_api.api.routes.v1.resources.suppliers import router as suppliers_router

router = APIRouter()
router.include_router(categories_router)
router.include_router(customers_router)
router.include_router(employees_router)
router.include_router(orders_router)
router.include_router(products_router)
router.include_router(shippers_router)
router.include_router(suppliers_router)
router.include_router(order_details_router)
