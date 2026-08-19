import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.core.db import db_manager
from app.core.redis_client import redis_manager
from app.core.kafka_client import kafka_manager
from app.api.v1.router import api_v1_router
from app.api.websockets.stream import router as ws_router

logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("condigence.server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup lifecycle
    logger.info(f"Starting {settings.APP_NAME} in [{settings.ENVIRONMENT}] mode...")
    await db_manager.connect()
    await redis_manager.connect()
    await kafka_manager.connect()
    yield
    # Shutdown lifecycle
    logger.info("Shutting down services...")
    await db_manager.disconnect()
    await redis_manager.disconnect()
    await kafka_manager.disconnect()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Condigence LLP AI Agentic Operations System - Multi-Agent Management Layer",
        version="1.0.0",
        lifespan=lifespan
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include REST routers & WebSocket routers
    app.include_router(api_v1_router)
    app.include_router(ws_router)

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "HEALTHY",
            "app_name": settings.APP_NAME,
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "database_connected": db_manager.is_connected,
            "redis_connected": redis_manager.is_connected,
            "kafka_connected": kafka_manager.is_connected
        }

    # Mount built frontend assets if dist exists
    dist_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
    if os.path.exists(dist_dir):
        app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            # Don't intercept API or doc routes
            if full_path.startswith(("api", "docs", "openapi.json", "health", "ws")):
                return None
            index_path = os.path.join(dist_dir, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
            return {"message": "Portal static build not found"}

    return app


app = create_app()
