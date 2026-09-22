"""Clinical screening and drawing inference endpoints."""

from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.logging import get_logger
from app.schemas.common import DrawingModality, ErrorResponse
from app.schemas.prediction import (
    DrawingPrediction,
    SessionPredictionResponse,
    SinglePredictionResponse,
)
from app.services.fusion import aggregate_screening_session
from app.services.image_processor import ImageProcessingError, process_image_bytes
from app.services.predictor import ModelNotReadyError, predict_drawing

router = APIRouter()
logger = get_logger("predict_endpoint")


@router.post(
    "/predict/single",
    response_model=SinglePredictionResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid image format or corrupted file",
        },
        503: {
            "model": ErrorResponse,
            "description": "Modality model not loaded into memory",
        },
    },
    summary="Predict Parkinson's probability for a single drawing",
    description=(
        "Uploads a single drawing image (Circle, Meander, or Spiral) and evaluates "
        "Parkinson's clinical screening indicators."
    ),
)
async def predict_single_drawing(
    file: UploadFile = File(..., description="Drawing image file (PNG, JPG, or WebP)"),
    modality: DrawingModality = Form(
        ..., description="Drawing examination modality ('circle', 'meander', 'spiral')"
    ),
    threshold: Optional[float] = Form(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional custom classification threshold (default: 0.50)",
    ),
) -> SinglePredictionResponse:
    """Evaluate an individual drawing image."""
    try:
        content = await file.read()
        tensor = process_image_bytes(
            file_bytes=content, filename=file.filename or "drawing.png"
        )
    except ImageProcessingError as err:
        logger.warning(f"Image validation rejected for '{file.filename}': {err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err

    try:
        prediction = predict_drawing(
            modality=modality, image_tensor=tensor, threshold=threshold
        )
    except ModelNotReadyError as err:
        logger.error(f"Inference rejected due to unloaded model: {err}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(err)
        ) from err

    return SinglePredictionResponse(
        prediction=prediction,
        timestamp=datetime.now(timezone.utc),
    )


@router.post(
    "/predict/session",
    response_model=SessionPredictionResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "One or more uploaded images are invalid",
        },
        503: {
            "model": ErrorResponse,
            "description": "One or more models are not ready",
        },
    },
    summary="Execute full multi-modal screening session (Circle + Meander + Spiral)",
    description=(
        "Uploads all three required clinical drawing modalities simultaneously "
        "and computes an aggregate screening outcome via Simple Average Late Fusion."
    ),
)
async def predict_screening_session(
    circle_file: UploadFile = File(..., description="Circle drawing test image"),
    meander_file: UploadFile = File(
        ..., description="Meander continuous wave drawing image"
    ),
    spiral_file: UploadFile = File(..., description="Archimedean spiral drawing image"),
    threshold: Optional[float] = Form(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional custom screening decision threshold (default: 0.50)",
    ),
) -> SessionPredictionResponse:
    """Execute complete 3-drawing screening examination and compute late fusion."""
    files_map = {
        DrawingModality.CIRCLE: circle_file,
        DrawingModality.MEANDER: meander_file,
        DrawingModality.SPIRAL: spiral_file,
    }

    drawings: Dict[DrawingModality, DrawingPrediction] = {}

    for modality, upload in files_map.items():
        try:
            content = await upload.read()
            tensor = process_image_bytes(
                file_bytes=content, filename=upload.filename or f"{modality.value}.png"
            )
        except ImageProcessingError as err:
            logger.warning(
                f"Validation failed for modality '{modality.value}' in session: {err}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {modality.value} image: {err}",
            ) from err

        try:
            pred = predict_drawing(
                modality=modality, image_tensor=tensor, threshold=threshold
            )
            drawings[modality] = pred
        except ModelNotReadyError as err:
            logger.error(f"Session inference rejected, model not ready: {err}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(err)
            ) from err

    try:
        session_result = aggregate_screening_session(
            drawings=drawings, threshold=threshold
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err

    return session_result
