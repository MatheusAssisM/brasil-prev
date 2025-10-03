from typing import AsyncGenerator
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.infrastructure.api.routes import router
from app.infrastructure.api.rate_limiter import limiter, rate_limit_exceeded_handler
from app.core.config import settings
from app.infrastructure.logging.logger import setup_logging
from app.infrastructure.di.container import get_logger

setup_logging(settings.LOG_LEVEL)
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator:  # pylint: disable=unused-argument
    # Startup
    yield
    # Shutdown
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "A simplified Monopoly-style board game simulation API "
        "with clean architecture and strategy pattern"
    ),
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url=settings.DOC_URL,
    lifespan=lifespan,
)

# Configure rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(router)


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "monopoly-simulator-api",
            "version": "1.0.0",
        }
    )


def start() -> None:
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    start()
