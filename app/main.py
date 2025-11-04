from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.endpoints.health import router as health_router
from app.api.routes import api_router
from app.core.database import create_tables
from app.core.errors import (
    ApiError,
    api_error_handler,
    global_exception_handler,
    http_exception_handler,
    starlette_http_exception_handler,
    validation_error_handler,
)
from app.core.secrets import setup_secrets
from app.core.security import limiter

app = FastAPI(
    title="Reading List API",
    version="0.1.0",
    description="API для управления списком книг и статей к прочтению",
    docs_url="/docs",
    redoc_url="/redoc",
)

secrets_initialized = setup_secrets()
if not secrets_initialized:
    print("Warning: Running with missing secrets (development mode)")

create_tables()

app.state.limiter = limiter

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(health_router, prefix="/api/v1")

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Reading List API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
