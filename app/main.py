from typing import Dict

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import settings

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
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    start()
