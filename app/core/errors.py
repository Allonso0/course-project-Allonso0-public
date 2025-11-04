import uuid
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApiError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status: int = 400,
        details: Any = None,
        error_type: str = "about:blank",
    ):
        self.code = code
        self.message = message
        self.status = status
        self.details = details
        self.error_type = error_type
        self.correlation_id = str(uuid.uuid4())


class NotFoundError(ApiError):
    def __init__(self, resource: str = "Resource", details: Any = None):
        super().__init__(
            code="not_found",
            message=f"{resource} not found",
            status=404,
            details=details,
            error_type="/errors/not-found",
        )


class ValidationError(ApiError):
    def __init__(self, message: str = "Validation error", details: Any = None):
        super().__init__(
            code="validation_error",
            message=message,
            status=422,
            details=details,
            error_type="/errors/validation",
        )


def create_problem_detail(
    status: int,
    title: str,
    detail: str,
    error_type: str = "about:blank",
    correlation_id: Optional[str] = None,
    extras: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload = {
        "type": error_type,
        "title": title,
        "status": status,
        "detail": detail,
        "correlation_id": correlation_id or str(uuid.uuid4()),
    }
    if extras:
        payload.update(extras)
    return payload


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    error_payload = create_problem_detail(
        status=exc.status,
        title=exc.code.replace("_", " ").title(),
        detail=exc.message,
        error_type=exc.error_type,
        correlation_id=exc.correlation_id,
        extras=(
            {"error_code": exc.code, "details": exc.details} if exc.details else None
        ),
    )

    return JSONResponse(
        status_code=exc.status,
        content=error_payload,
        headers={"Content-Type": "application/problem+json"},
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field = first_error.get("loc", ["unknown"])[-1]

    error_payload = create_problem_detail(
        status=422,
        title="Validation Error",
        detail=f"Validation error for field {field}",
        error_type="/errors/validation",
        extras={"error_code": "validation_error", "validation_details": errors},
    )

    return JSONResponse(
        status_code=422,
        content=error_payload,
        headers={"Content-Type": "application/problem+json"},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "HTTP error occurred"

    error_payload = create_problem_detail(
        status=exc.status_code,
        title="HTTP Error",
        detail=detail,
        error_type="/errors/http",
        extras={"error_code": "http_error"},
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload,
        headers={"Content-Type": "application/problem+json"},
    )


async def starlette_http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    if exc.status_code == 404:
        error_type = "/errors/not-found"
        title = "Not Found"
        detail = "The requested resource was not found"
    elif exc.status_code == 405:
        error_type = "/errors/method-not-allowed"
        title = "Method Not Allowed"
        detail = "The method is not allowed for the requested URL"
    else:
        error_type = "/errors/http"
        title = "HTTP Error"
        detail = exc.detail if isinstance(exc.detail, str) else "An error occurred"

    error_payload = create_problem_detail(
        status=exc.status_code,
        title=title,
        detail=detail,
        error_type=error_type,
        extras={"error_code": f"http_{exc.status_code}"},
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload,
        headers={"Content-Type": "application/problem+json"},
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_payload = create_problem_detail(
        status=500,
        title="Internal Server Error",
        detail="An internal server error occurred",
        error_type="/errors/internal",
    )

    print(f"Unhandled exception: {exc}")

    return JSONResponse(
        status_code=500,
        content=error_payload,
        headers={"Content-Type": "application/problem+json"},
    )
