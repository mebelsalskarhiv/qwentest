from fastapi import APIRouter
from app.api.v1.endpoints import auth, inventory, production, hr, users
from app.api.v1.superadmin import tenants

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(inventory.router)
api_router.include_router(production.router)
api_router.include_router(hr.router)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tenants.router, prefix="/superadmin", tags=["superadmin"])
