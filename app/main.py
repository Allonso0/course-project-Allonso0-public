from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import api_router
from app.core.errors import ApiError, api_error_handler, http_exception_handler

app = FastAPI(
    title="SecDev Course App",
    version="0.1.0",
    description="API для управления списком книг и статей к прочтению",
)

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, api_error_handler)
app.add_exception_handler(404, http_exception_handler)

app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Reading List API",
        "version": "0.1.0",
        "health": "/health",
    }


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "not_found", "message": "Endpoint not found"}},
    )
