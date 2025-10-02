from typing import Dict

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import settings
from app.utils.logger import setup_logging, get_logger

# Initialize logging
setup_logging(settings.log_level)
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    description=(
        "A simplified Monopoly-style board game simulation API "
        "with clean architecture and strategy pattern"
    ),
    version="1.0.0",
    debug=settings.debug,
    docs_url=settings.doc_url
)

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info(
        "Application starting",
        extra={
            "app_name": settings.app_name,
            "log_level": settings.log_level,
            "debug": settings.debug,
            "host": settings.api_host,
            "port": settings.api_port
        }
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Application shutting down")


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
    """Start the FastAPI application with uvicorn."""
    logger.info(
        "Starting uvicorn server",
        extra={
            "host": settings.api_host,
            "port": settings.api_port,
            "reload": settings.debug
        }
    )

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    start()
