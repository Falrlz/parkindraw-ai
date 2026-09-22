"""Inference service for evaluating drawing tensors with loaded PyTorch models."""

from typing import Optional

import torch

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.common import DrawingModality, PredictionClass
from app.schemas.prediction import DrawingPrediction, Probabilities
from app.services.model_loader import model_registry

logger = get_logger("predictor")
settings = get_settings()


class ModelNotReadyError(RuntimeError):
    """Raised when an inference request is made for an unloaded modality model."""


def predict_drawing(
    modality: DrawingModality,
    image_tensor: torch.Tensor,
    threshold: Optional[float] = None,
) -> DrawingPrediction:
    """Execute forward inference pass and return structured clinical prediction.

    Args:
        modality: Drawing modality to evaluate ('circle', 'meander', 'spiral').
        image_tensor: Normalized 4D batch tensor of shape [1, 3, 224, 224].
        threshold: Decision threshold for positive Parkinson class
            (default from settings).

    Returns:
        DrawingPrediction: Structured prediction result containing
            probabilities and labels.

    Raises:
        ModelNotReadyError: If the requested modality model is not loaded in memory.
    """
    model = model_registry.get_model(modality.value)
    if model is None:
        raise ModelNotReadyError(
            f"Model for modality '{modality.value}' is not loaded or ready "
            f"for inference."
        )

    decision_threshold = (
        threshold if threshold is not None else settings.CLASSIFICATION_THRESHOLD
    )

    device = model_registry.device
    tensor_on_device = image_tensor.to(device)

    with torch.no_grad():
        logits = model(tensor_on_device)
        probabilities = torch.softmax(logits, dim=1).cpu().squeeze(0)

    prob_healthy = float(probabilities[0].item())
    prob_parkinson = float(probabilities[1].item())

    # Apply clinical classification decision boundary
    is_parkinson = prob_parkinson >= decision_threshold

    if is_parkinson:
        prediction = PredictionClass.PARKINSON
        prediction_code = 1
        confidence = prob_parkinson
    else:
        prediction = PredictionClass.HEALTHY
        prediction_code = 0
        confidence = prob_healthy

    logger.debug(
        f"Inference complete [{modality.value}]: label={prediction.value}, "
        f"P(Parkinson)={prob_parkinson:.4f}, P(Healthy)={prob_healthy:.4f}"
    )

    return DrawingPrediction(
        modality=modality,
        prediction=prediction,
        prediction_code=prediction_code,
        confidence=round(confidence, 4),
        probabilities=Probabilities(
            Healthy=round(prob_healthy, 4),
            Parkinson=round(prob_parkinson, 4),
        ),
    )
