"""Fixed preprocessing for ParkinDraw.

One definition, used by training, evaluation, and inference alike. Keeping a
single source prevents training-serving skew: an API that resizes or normalises
even slightly differently would silently produce different predictions.

The steps are locked by `0_LITERATURE_REVIEW.md` section 5 and must not vary
per experiment:

- convert to RGB,
- resize to 224x224 with bilinear interpolation,
- scale to [0, 1] and normalise with ImageNet statistics.

Square resizing is safe here: EDA measured a mean aspect ratio of 1.01, so the
geometric distortion is negligible and aspect-preserving padding is unnecessary.
"""

import torch
from PIL import Image
from torchvision.transforms import v2

IMAGE_SIZE = 224

# ResNet-18 is pretrained on ImageNet, so its own statistics must be used.
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def build_transform(extra: list | None = None) -> v2.Compose:
    """Return the fixed preprocessing pipeline.

    Deterministic by construction when `extra` is empty: the same image always
    maps to the same tensor.

    `extra` inserts steps between the resize and the tensor conversion, and
    exists so `parkindraw.preprocessing.augmentation` can add jitter without
    restating the fixed steps. Rebuilding that chain elsewhere would let the
    training and evaluation paths drift apart unnoticed, which is exactly what
    a single preprocessing definition is meant to prevent.
    """
    return v2.Compose(
        [
            v2.Resize(
                (IMAGE_SIZE, IMAGE_SIZE),
                interpolation=v2.InterpolationMode.BILINEAR,
            ),
            *(extra or []),
            v2.ToImage(),
            v2.ToDtype(dtype=torch.float32, scale=True),
            v2.Normalize(mean=list(IMAGENET_MEAN), std=list(IMAGENET_STD)),
        ]
    )


def load_image(path) -> Image.Image:
    """Open an image as RGB.

    Kept next to the transform because the colour conversion is part of the
    contract: the network always receives three channels, whatever the file
    happens to store.
    """
    with Image.open(path) as image:
        return image.convert("RGB")
