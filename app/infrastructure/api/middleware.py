from fastapi import Request, status
from fastapi.responses import JSONResponse, Response
from typing import Callable, Union

from app.core.exceptions import (
    GameError,
    GameConfigurationError,
    InvalidGameStateError,
    InvalidMoveError,
    InvalidPropertyError,
    InvalidPlayerError,
)


async def error_handler_middleware(request: Request, call_next: Callable) -> Union[Response, JSONResponse]:
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
    except GameConfigurationError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "ConfigurationError",
                "message": str(exc),
                "detail": "Invalid game configuration parameters",
            },
        )
    except InvalidGameStateError as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "InvalidGameState",
                "message": str(exc),
                "detail": "Game is in an invalid state for this operation",
            },
        )
    except InvalidMoveError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "InvalidMove",
                "message": str(exc),
                "detail": "Invalid move parameters",
            },
        )
    except InvalidPropertyError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "InvalidProperty",
                "message": str(exc),
                "detail": "Invalid property parameters",
            },
        )
    except InvalidPlayerError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "InvalidPlayer",
                "message": str(exc),
                "detail": "Invalid player parameters",
            },
        )
    except GameError as exc:
        # Catch-all for other game errors
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "GameError",
                "message": str(exc),
                "detail": "An error occurred during game execution",
            },
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "ValueError",
                "message": str(exc),
                "detail": "Invalid value provided",
            },
        )
    except TypeError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "TypeError",
                "message": str(exc),
                "detail": "Invalid type provided",
            },
        )
    except Exception as exc:
        # Catch-all for unexpected errors
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "detail": str(exc),
            },
        )
