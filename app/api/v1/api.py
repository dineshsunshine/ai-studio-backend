from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, admin, admin_defaults, settings, models, looks

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(admin_defaults.router, prefix="/admin", tags=["admin-defaults"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(looks.router, prefix="/looks", tags=["looks"])

