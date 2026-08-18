from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.vehicles.router import router as vehicles_router
from app.modules.commissions.router import router as commissions_router
from app.modules.trips.router import router as trips_router
from app.modules.fuel.router import router as fuel_router
from app.modules.maintenance.router import router as maintenance_router
from app.modules.reports.router import router as reports_router
router = APIRouter()

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(vehicles_router)
router.include_router(commissions_router)
router.include_router(trips_router)
router.include_router(fuel_router)
router.include_router(maintenance_router)
router.include_router(reports_router)
