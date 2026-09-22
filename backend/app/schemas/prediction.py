"""Prediction and clinical screening payload schemas."""

from datetime import datetime
from typing import Dict

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import CLINICAL_DISCLAIMER, DrawingModality, PredictionClass


class Probabilities(BaseModel):
    """Softmax class probabilities dictionary."""

    Healthy: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Estimated probability that subject is Healthy (Class 0)",
    )
    Parkinson: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Estimated probability that subject has Parkinson's (Class 1)",
    )


class DrawingPrediction(BaseModel):
    """Prediction outcome for an individual drawing modality."""

    modality: DrawingModality = Field(..., description="Drawing test modality")
    prediction: PredictionClass = Field(..., description="Categorical prediction label")
    prediction_code: int = Field(
        ...,
        ge=0,
        le=1,
        description="Numeric prediction label (0 = Healthy, 1 = Parkinson)",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the predicted class (highest probability)",
    )
    probabilities: Probabilities = Field(
        ..., description="Full class probability distribution"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "modality": "spiral",
                "prediction": "Parkinson",
                "prediction_code": 1,
                "confidence": 0.9425,
                "probabilities": {
                    "Healthy": 0.0575,
                    "Parkinson": 0.9425,
                },
            }
        }
    )


class SinglePredictionResponse(BaseModel):
    """Envelope response for single drawing prediction."""

    prediction: DrawingPrediction = Field(..., description="Inference result")
    clinical_disclaimer: str = Field(
        default=CLINICAL_DISCLAIMER,
        description="Mandatory medical screening disclaimer",
    )
    timestamp: datetime = Field(..., description="Inference timestamp (UTC)")


class SessionPredictionResponse(BaseModel):
    """Envelope response for complete multi-modal screening session."""

    session_id: str = Field(..., description="Unique UUID identifier for this session")
    fusion_prediction: PredictionClass = Field(
        ..., description="Aggregated screening label from late fusion"
    )
    fusion_prediction_code: int = Field(
        ..., description="Aggregated numeric label (0 = Healthy, 1 = Parkinson)"
    )
    fusion_probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Arithmetic mean of Parkinson probabilities across all 3 modalities",
    )
    threshold: float = Field(
        ..., description="Decision threshold applied for positive screening"
    )
    drawings: Dict[str, DrawingPrediction] = Field(
        ..., description="Individual drawing results keyed by modality name"
    )
    clinical_disclaimer: str = Field(
        default=CLINICAL_DISCLAIMER,
        description="Mandatory medical screening disclaimer",
    )
    timestamp: datetime = Field(..., description="Screening session timestamp (UTC)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                "fusion_prediction": "Parkinson",
                "fusion_prediction_code": 1,
                "fusion_probability": 0.8950,
                "threshold": 0.50,
                "drawings": {
                    "circle": {
                        "modality": "circle",
                        "prediction": "Parkinson",
                        "prediction_code": 1,
                        "confidence": 0.8800,
                        "probabilities": {"Healthy": 0.1200, "Parkinson": 0.8800},
                    },
                    "meander": {
                        "modality": "meander",
                        "prediction": "Parkinson",
                        "prediction_code": 1,
                        "confidence": 0.8650,
                        "probabilities": {"Healthy": 0.1350, "Parkinson": 0.8650},
                    },
                    "spiral": {
                        "modality": "spiral",
                        "prediction": "Parkinson",
                        "prediction_code": 1,
                        "confidence": 0.9400,
                        "probabilities": {"Healthy": 0.0600, "Parkinson": 0.9400},
                    },
                },
                "clinical_disclaimer": CLINICAL_DISCLAIMER,
                "timestamp": "2026-09-22T14:30:00Z",
            }
        }
    )
