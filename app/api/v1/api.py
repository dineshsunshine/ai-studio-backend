from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, admin, admin_defaults, settings, models, looks, links, bootstrap, migrate, subscription, admin_subscription

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(bootstrap.router, prefix="/bootstrap", tags=["bootstrap"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(admin_defaults.router, prefix="/admin", tags=["admin-defaults"])
api_router.include_router(admin_subscription.router, prefix="/admin", tags=["admin-subscription"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(subscription.router, prefix="/subscription", tags=["subscription"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(looks.router, prefix="/looks", tags=["looks"])
api_router.include_router(links.router, prefix="/links", tags=["links"])
api_router.include_router(migrate.router, prefix="/migrate", tags=["migration"])

