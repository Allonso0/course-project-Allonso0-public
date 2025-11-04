from fastapi import APIRouter, Request

from app.core.security import ENDPOINT_LIMITS, limiter

router = APIRouter()


@router.get("/health")
@limiter.limit(
    ENDPOINT_LIMITS["health_check"] if ENDPOINT_LIMITS["health_check"] else None
)
async def health_check(request: Request):
    return {"status": "ok", "service": "Reading List API"}
