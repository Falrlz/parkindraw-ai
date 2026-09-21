"""Conservative clinical data augmentation for training drawings."""

from torchvision.transforms import v2

from src.config.config import (
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
    MAX_ROTATION_DEGREES,
    MAX_TRANSLATE_FRACTION,
    PAPER_FILL,
    SCALE_RANGE,
)


def augmentation(
    max_rotation: float = MAX_ROTATION_DEGREES,
    max_translate: float = MAX_TRANSLATE_FRACTION,
    scale_range: tuple[float, float] = SCALE_RANGE,
    fill: int = PAPER_FILL,
    ) -> v2.RandomAffine:

    """Return geometric affine jitter (small rotation, shift, scale; no horizontal flip)."""
    return v2.RandomAffine(
        degrees=max_rotation,
        translate=(max_translate, max_translate),
        scale=scale_range,
        interpolation=v2.InterpolationMode.BILINEAR,
        fill=fill,
    )


# Alias for backward compatibility
build_augmentation = augmentation


def build_train_transform(
    image_size: int = IMAGE_SIZE,
    mean: tuple[float, float, float] = IMAGENET_MEAN,
    std: tuple[float, float, float] = IMAGENET_STD,
    **aug_kwargs,
    ) -> v2.Compose:

    """Return the complete training pipeline: fixed preprocessing combined with affine jitter."""
    from src.preprocessing.transforms import transform

    base = transform(image_size=image_size, mean=mean, std=std)
    aug = augmentation(**aug_kwargs)
    return v2.Compose([base.transforms[0], aug, *base.transforms[1:]])
