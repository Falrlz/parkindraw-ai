"""Common schemas, enums, and constants for API payloads."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

CLINICAL_DISCLAIMER: str = (
    "ParkinDraw is an AI-assisted screening research tool, not an autonomous "
    "diagnostic medical device. Predictions should be evaluated alongside "
    "comprehensive clinical neurological assessments."
)


class DrawingModality(str, Enum):
    """Permissible drawing examination modalities."""

    CIRCLE = "circle"
    MEANDER = "meander"
    SPIRAL = "spiral"


class PredictionClass(str, Enum):
    """Categorical class labels."""

    HEALTHY = "Healthy"
    PARKINSON = "Parkinson"


class ErrorResponse(BaseModel):
    """Standardized error payload schema."""

    detail: str = Field(..., description="Human-readable explanation of the error")
    code: Optional[str] = Field(default=None, description="Machine-readable error code")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Uploaded file is corrupted or not a valid image.",
                "code": "INVALID_IMAGE_FILE",
            }
        }
    )
