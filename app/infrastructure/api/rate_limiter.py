from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import settings


def _rate_limit_key_func(request: Request) -> str:
    """
    Key function for rate limiting based on client IP address.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address as the rate limit key
    """
    return get_remote_address(request)


# Configure rate limiter
limiter = Limiter(
    key_func=_rate_limit_key_func,
    enabled=settings.RATE_LIMIT_ENABLED,
    storage_uri="memory://",
    strategy="fixed-window",
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors.

    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception

    Returns:
        JSONResponse with 429 status code and error details
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": "Too many requests. Please try again later.",
            "retry_after": exc.retry_after if hasattr(exc, "retry_after") else None,
        },
    )
