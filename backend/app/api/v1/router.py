# from fastapi import APIRouter

# from app.modules.users.router import router as users_router


# router = APIRouter()

# router.include_router(users_router)

from fastapi import APIRouter
from app.modules.vehicles.router import router as vehicles_router
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router


router = APIRouter()

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(vehicles_router)