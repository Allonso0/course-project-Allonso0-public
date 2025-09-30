from typing import Any, Dict

from fastapi import HTTPException, Request
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


class ValidationError(ApiError):
    def __init__(self, message: str = "Validation error", details: Any = None):
        super().__init__(
            code="validation_error", message=message, status=422, details=details
        )


class AuthorizationError(ApiError):
    def __init__(self, message: str = "Authorization required"):
        super().__init__(code="authorization_error", message=message, status=401)


class PermissionError(ApiError):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(code="permission_error", message=message, status=403)


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    response_content: Dict[str, Any] = {
        "error": {"code": exc.code, "message": exc.message}
    }

    if exc.details:
        response_content["error"]["details"] = exc.details

    return JSONResponse(status_code=exc.status, content=response_content)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": detail}},
    )
