from typing import Any, Dict

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400, details: Any = None):
        self.code = code
        self.message = message
        self.status = status
        self.details = details


class NotFoundError(ApiError):
    def __init__(self, resource: str = "Resource", details: Any = None):
        super().__init__(
            code="not_found",
            message=f"{resource} not found",
            status=404,
            details=details,
        )


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    response_content: Dict[str, Any] = {
        "error": {"code": exc.code, "message": exc.message}
    }

    if exc.details:
        response_content["error"]["details"] = exc.details

    return JSONResponse(status_code=exc.status, content=response_content)


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    first_error = errors[0] if errors else {}

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": f"Validation error for field {first_error.get('loc', ['unknown'])[-1]}",
                "details": errors,
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": detail}},
    )
