from typing import Callable, Dict, Tuple, Type, Union

from fastapi import Request, status
from fastapi.responses import JSONResponse, Response

from app.core.exceptions import (
    GameError,
    GameConfigurationError,
    InvalidGameStateError,
    InvalidMoveError,
    InvalidPropertyError,
    InvalidPlayerError,
)

EXCEPTION_MAP: Dict[Type[Exception], Tuple[int, str, str]] = {
    GameConfigurationError: (
        status.HTTP_400_BAD_REQUEST,
        "ConfigurationError",
        "Invalid game configuration parameters",
    ),
    InvalidGameStateError: (
        status.HTTP_409_CONFLICT,
        "InvalidGameState",
        "Game is in an invalid state for this operation",
    ),
    InvalidMoveError: (
        status.HTTP_400_BAD_REQUEST,
        "InvalidMove",
        "Invalid move parameters",
    ),
    InvalidPropertyError: (
        status.HTTP_400_BAD_REQUEST,
        "InvalidProperty",
        "Invalid property parameters",
    ),
    InvalidPlayerError: (
        status.HTTP_400_BAD_REQUEST,
        "InvalidPlayer",
        "Invalid player parameters",
    ),
    GameError: (
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "GameError",
        "An error occurred during game execution",
    ),
    ValueError: (status.HTTP_400_BAD_REQUEST, "ValueError", "Invalid value provided"),
    TypeError: (status.HTTP_400_BAD_REQUEST, "TypeError", "Invalid type provided"),
}


def _build_error_response(exc: Exception) -> JSONResponse:
    """Build error response from exception using mapping."""
    for exc_type, (status_code, error_name, detail) in EXCEPTION_MAP.items():
        if isinstance(exc, exc_type):
            return JSONResponse(
                status_code=status_code,
                content={"error": error_name, "message": str(exc), "detail": detail},
            )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "detail": str(exc),
        },
    )


async def error_handler_middleware(
    request: Request, call_next: Callable
) -> Union[Response, JSONResponse]:
    """
    Middleware to handle domain exceptions and translate them to HTTP responses.

    Args:
        request: The incoming HTTP request
        call_next: The next middleware or route handler

    Returns:
        JSONResponse with appropriate status code and error details
    """
    try:
        response: Response = await call_next(request)
        return response
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return _build_error_response(exc)
