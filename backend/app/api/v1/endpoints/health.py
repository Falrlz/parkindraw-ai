"""Health check and service status endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthResponse, ModelStatus
from app.services.model_loader import model_registry

router = APIRouter()
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check service health and model readiness",
    description=(
        "Returns overall backend health status, active compute device, "
        "and in-memory model readiness."
    ),
)
def get_health() -> HealthResponse:
    """Retrieve service health and model availability status."""
    status_map = model_registry.get_status()
    all_loaded = all(status_map.values())
    overall_status = "ok" if all_loaded else "degraded"

    return HealthResponse(
        status=overall_status,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc),
        device=str(model_registry.device),
        models=ModelStatus(
            circle=status_map["circle"],
            meander=status_map["meander"],
            spiral=status_map["spiral"],
        ),
        all_models_loaded=all_loaded,
    )
