"""Main FastAPI application factory and lifespan manager."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.api.v1.endpoints.health import get_health
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.schemas.health import HealthResponse
from app.services.model_loader import model_registry

settings = get_settings()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager handling startup and shutdown."""
    # Startup: configure logging and load PyTorch model weights
    setup_logging(level=settings.LOG_LEVEL)
    logger.info(f"Initializing {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Active environment: {settings.ENVIRONMENT}")

    # Load canonical ResNet-18 checkpoints
    model_registry.load_all_models(
        models_dir=settings.MODELS_DIR,
        preferred_device=settings.DEVICE,
    )

    yield

    # Shutdown logic
    logger.info("Shutting down ParkinDraw AI Backend service.")


def create_application() -> FastAPI:
    """Instantiate and configure the FastAPI application."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=(
            "AI-assisted clinical screening service for Parkinson's disease using "
            "Circle, Meander, and Spiral handwriting drawing analysis."
        ),
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure Cross-Origin Resource Sharing (CORS)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Root service descriptor
    @application.get(
        "/",
        summary="Service Descriptor",
        tags=["Root"],
    )
    def root() -> Dict[str, str]:
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs": "/docs",
            "health": "/health",
            "api_v1": settings.API_V1_STR,
        }

    # Root-level health check shortcut
    @application.get(
        "/health",
        response_model=HealthResponse,
        summary="Root Health Check",
        tags=["Root"],
    )
    def root_health() -> HealthResponse:
        return get_health()

    # Mount API v1 router
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()
