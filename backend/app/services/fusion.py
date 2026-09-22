"""Multi-modal late fusion service for aggregate clinical screening."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.common import CLINICAL_DISCLAIMER, DrawingModality, PredictionClass
from app.schemas.prediction import DrawingPrediction, SessionPredictionResponse

logger = get_logger("fusion")
settings = get_settings()


def aggregate_screening_session(
    drawings: Dict[DrawingModality, DrawingPrediction],
    threshold: Optional[float] = None,
    session_id: Optional[str] = None,
) -> SessionPredictionResponse:
    """Combine multi-modal drawing predictions via Simple Average Late Fusion.

    Computes the arithmetic mean of Parkinson probabilities across Circle,
    Meander, and Spiral modalities:
        P_fusion(Parkinson) = (P_circle + P_meander + P_spiral) / 3.0

    Args:
        drawings: Dictionary mapping drawing modality to individual prediction.
        threshold: Decision threshold for positive screening (default: 0.50).
        session_id: Optional pre-assigned session UUID string.

    Returns:
        SessionPredictionResponse: Unified clinical screening session outcome.

    Raises:
        ValueError: If any required modality is missing from the input mapping.
    """
    required_modalities = {
        DrawingModality.CIRCLE,
        DrawingModality.MEANDER,
        DrawingModality.SPIRAL,
    }
    provided_modalities = set(drawings.keys())

    missing = required_modalities - provided_modalities
    if missing:
        missing_names = ", ".join(m.value for m in missing)
        raise ValueError(
            f"Screening session requires all 3 modalities. Missing: {missing_names}."
        )

    decision_threshold = (
        threshold if threshold is not None else settings.CLASSIFICATION_THRESHOLD
    )

    # Compute unweighted arithmetic mean of Parkinson probabilities
    parkinson_probs = [
        drawings[modality].probabilities.Parkinson for modality in required_modalities
    ]
    fusion_prob = sum(parkinson_probs) / float(len(parkinson_probs))

    is_parkinson = fusion_prob >= decision_threshold
    fusion_prediction = (
        PredictionClass.PARKINSON if is_parkinson else PredictionClass.HEALTHY
    )
    fusion_code = 1 if is_parkinson else 0

    assigned_id = session_id or str(uuid.uuid4())
    current_time = datetime.now(timezone.utc)

    # Format output dictionary with string keys for JSON compliance
    string_keyed_drawings = {
        modality.value: drawings[modality] for modality in drawings
    }

    logger.info(
        f"Aggregated screening session [{assigned_id}]: outcome={fusion_prediction.value}, "
        f"fusion_prob={fusion_prob:.4f} (threshold={decision_threshold})"
    )

    return SessionPredictionResponse(
        session_id=assigned_id,
        fusion_prediction=fusion_prediction,
        fusion_prediction_code=fusion_code,
        fusion_probability=round(fusion_prob, 4),
        threshold=decision_threshold,
        drawings=string_keyed_drawings,
        clinical_disclaimer=CLINICAL_DISCLAIMER,
        timestamp=current_time,
    )
