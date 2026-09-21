"""Deterministic image preprocessing pipeline for evaluation and inference."""

from pathlib import Path

import torch
from PIL import Image
from torchvision.transforms import v2

from src.config.config import (
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
)


def transform(
    image_size: int = IMAGE_SIZE,
    mean: tuple[float, float, float] = IMAGENET_MEAN,
    std: tuple[float, float, float] = IMAGENET_STD,
    ) -> v2.Compose:

    """Return the deterministic preprocessing pipeline (Resize + ImageNet Normalization)."""
    return v2.Compose(
        [
            v2.Resize(
                (image_size, image_size),
                interpolation=v2.InterpolationMode.BILINEAR,
            ),
            v2.ToImage(),
            v2.ToDtype(dtype=torch.float32, scale=True),
            v2.Normalize(mean=list(mean), std=list(std)),
        ]
    )


# Alias for backward compatibility
build_transform = transform


def load_image(
    path: str | Path
    ) -> Image.Image:

    """Load image from disk and ensure standard 3-channel RGB format."""
    with Image.open(path) as image:
        return image.convert("RGB")
