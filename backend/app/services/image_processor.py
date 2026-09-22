"""In-memory image processing and validation service.

Converts raw image file streams into canonical normalized PyTorch tensors
matching the training evaluation preprocessing pipeline.
"""

import io
from pathlib import Path
from typing import Tuple

import torch
from PIL import Image, UnidentifiedImageError
from torchvision import transforms

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("image_processor")
settings = get_settings()

# Canonical ImageNet normalization constants used across ParkinDraw ML
IMAGENET_MEAN: Tuple[float, float, float] = (0.485, 0.456, 0.406)
IMAGENET_STD: Tuple[float, float, float] = (0.229, 0.224, 0.225)
TARGET_IMAGE_SIZE: Tuple[int, int] = (224, 224)

# Deterministic PyTorch inference pipeline
INFERENCE_TRANSFORM = transforms.Compose(
    [
        transforms.Resize(
            TARGET_IMAGE_SIZE,
            interpolation=transforms.InterpolationMode.BILINEAR,
            antialias=True,
        ),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ]
)


class ImageProcessingError(ValueError):
    """Raised when an uploaded file cannot be parsed or validated as a valid image."""


def validate_image_metadata(filename: str, file_size: int) -> None:
    """Validate uploaded file metadata against security and size constraints.

    Args:
        filename: Name of the uploaded file.
        file_size: Size of the payload in bytes.

    Raises:
        ImageProcessingError: If extension is disallowed or file size exceeds limits.
    """
    extension = Path(filename).suffix.lower()
    if extension not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise ImageProcessingError(
            f"File extension '{extension}' is not permitted. "
            f"Supported formats: {', '.join(sorted(settings.ALLOWED_IMAGE_EXTENSIONS))}."
        )

    if file_size <= 0:
        raise ImageProcessingError("Uploaded image file is empty (0 bytes).")

    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        max_mb = settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        raise ImageProcessingError(
            f"Image file size ({actual_mb:.2f} MB) exceeds maximum allowed limit ({max_mb:.1f} MB)."
        )


def process_image_bytes(
    file_bytes: bytes, filename: str = "drawing.png"
) -> torch.Tensor:
    """Validate, decode, and transform raw image bytes into an inference tensor.

    Args:
        file_bytes: Raw bytes of the uploaded drawing image.
        filename: Original filename used for extension validation.

    Returns:
        torch.Tensor: Preprocessed batch tensor of shape [1, 3, 224, 224].

    Raises:
        ImageProcessingError: If image cannot be read, decoded, or is corrupted.
    """
    validate_image_metadata(filename=filename, file_size=len(file_bytes))

    try:
        # Open in-memory byte buffer
        stream = io.BytesIO(file_bytes)
        with Image.open(stream) as img:
            # Force decoding to detect truncated/corrupt bitstreams immediately
            img.load()
            # Ensure 3-channel RGB representation (converts RGBA, Grayscale, Palette)
            rgb_img = img.convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError) as err:
        logger.warning(f"Failed to decode uploaded image '{filename}': {err}")
        raise ImageProcessingError(
            f"Uploaded file '{filename}' could not be decoded as a valid image: {err}"
        ) from err

    # Apply deterministic transforms
    tensor = INFERENCE_TRANSFORM(rgb_img)

    # Add batch dimension -> shape: [1, 3, 224, 224]
    batched_tensor = tensor.unsqueeze(0)
    return batched_tensor
