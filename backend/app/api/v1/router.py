from fastapi import APIRouter
from app.api.v1.endpoints import auth, inventory, production, hr

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(inventory.router)
api_router.include_router(production.router)
api_router.include_router(hr.router)
