from fastapi import APIRouter

from pilot_api.api.routes.v1.resources.categories import router as categories_router
# from pilot_api.api.routes.v1.resources.customer_customer_demo import router as customer_customer_demo_router
# from pilot_api.api.routes.v1.resources.customer_demographics import router as customer_demographics_router
from pilot_api.api.routes.v1.resources.customers import router as customers_router
# from pilot_api.api.routes.v1.resources.employee_territories import router as employee_territories_router
from pilot_api.api.routes.v1.resources.employees import router as employees_router
from pilot_api.api.routes.v1.resources.order_details import router as order_details_router
from pilot_api.api.routes.v1.resources.orders import router as orders_router
from pilot_api.api.routes.v1.resources.products import router as products_router
# from pilot_api.api.routes.v1.resources.regions import router as regions_router
from pilot_api.api.routes.v1.resources.shippers import router as shippers_router
from pilot_api.api.routes.v1.resources.suppliers import router as suppliers_router
# from pilot_api.api.routes.v1.resources.territories import router as territories_router

router = APIRouter()
router.include_router(categories_router)
# router.include_router(customer_demographics_router)
# router.include_router(customer_customer_demo_router)
router.include_router(customers_router)
# router.include_router(employee_territories_router)
router.include_router(employees_router)
router.include_router(orders_router)
router.include_router(products_router)
# router.include_router(regions_router)
router.include_router(shippers_router)
router.include_router(suppliers_router)
# router.include_router(territories_router)
router.include_router(order_details_router)
