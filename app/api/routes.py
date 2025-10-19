from fastapi import APIRouter

from app.api.endpoints import entries, health, uploads

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(entries.router, prefix="/entries", tags=["entries"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
