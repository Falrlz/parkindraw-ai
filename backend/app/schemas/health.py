"""Health and readiness check schemas."""

from datetime import datetime
from typing import Dict

from pydantic import BaseModel, ConfigDict, Field


class ModelStatus(BaseModel):
    """Availability status flags for each modality model."""

    circle: bool = Field(..., description="Whether circle model is loaded and ready")
    meander: bool = Field(..., description="Whether meander model is loaded and ready")
    spiral: bool = Field(..., description="Whether spiral model is loaded and ready")


class HealthResponse(BaseModel):
    """Health check response payload."""

    status: str = Field(..., description="Overall system health status ('ok' or 'degraded')")
    version: str = Field(..., description="Application semantic version")
    environment: str = Field(..., description="Active runtime environment")
    timestamp: datetime = Field(..., description="Current UTC server timestamp")
    device: str = Field(..., description="PyTorch active compute device ('cuda' or 'cpu')")
    models: ModelStatus = Field(..., description="Availability status per modality")
    all_models_loaded: bool = Field(
        ..., description="True if all three drawing models are loaded into memory"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "version": "0.1.0",
                "environment": "development",
                "timestamp": "2026-09-22T14:30:00Z",
                "device": "cpu",
                "models": {
                    "circle": True,
                    "meander": True,
                    "spiral": True,
                },
                "all_models_loaded": True,
            }
        }
    )
