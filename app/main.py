from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.endpoints.health import router as health_router
from app.api.routes import api_router
from app.core.errors import (
    ApiError,
    api_error_handler,
    http_exception_handler,
    validation_error_handler,
)

app = FastAPI(
    title="Reading List API",
    version="0.1.0",
    description="API для управления списком книг и статей к прочтению",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

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
