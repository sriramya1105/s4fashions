import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger("threadcraft_security")


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Standardized, clean 429 response when rate limits are breached (CWE-307).
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate Limit Exceeded",
            "message": "Too many requests. Please slow down and try again later.",
            "retry_after": exc.detail
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Standardizes HTTP exceptions with safe messages.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Request Error",
            "status_code": exc.status_code,
            "message": exc.detail
        },
        headers=getattr(exc, "headers", None)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles Pydantic input validation errors without leaking server internals (CWE-20).
    """
    cleaned_errors = []
    for err in exc.errors():
        cleaned_errors.append({
            "field": " -> ".join([str(loc) for loc in err.get("loc", [])]),
            "issue": err.get("msg")
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Input validation failed. Please check payload fields.",
            "details": cleaned_errors
        }
    )


async def global_unhandled_exception_handler(request: Request, exc: Exception):
    """
    CWE-209 Defense: Intercepts unhandled crashes, SQL syntax errors, or null pointers.
    Logs the real error internally for administrators, but returns a generic safe message
    to the client so database schema or filesystem paths are NEVER exposed.
    """
    logger.error(f"Unhandled Exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. The security team has been notified. No internal state disclosed."
        }
    )
