"""Tests for the fixed preprocessing and the training augmentation."""

import torch

from parkindraw.data.dataset import build_manifest
from parkindraw.preprocessing.augmentation import build_train_transform
from parkindraw.preprocessing.transforms import (
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
    build_transform,
    load_image,
)


def _sample(raw_dir):
    manifest = build_manifest(raw_dir)
    return load_image(raw_dir / manifest.filepath.iloc[0])


# --- Fixed preprocessing --------------------------------------------------


def test_image_is_loaded_as_rgb(raw_dir):
    assert _sample(raw_dir).mode == "RGB"


def test_output_shape_matches_resnet_input(raw_dir):
    tensor = build_transform()(_sample(raw_dir))
    assert tensor.shape == (3, IMAGE_SIZE, IMAGE_SIZE)


def test_output_is_a_float_tensor(raw_dir):
    assert build_transform()(_sample(raw_dir)).dtype == torch.float32


def test_preprocessing_is_deterministic(raw_dir):
    """The same image must always map to the same tensor."""
    image = _sample(raw_dir)
    transform = build_transform()
    assert torch.equal(transform(image), transform(image))


def test_normalisation_uses_imagenet_statistics(raw_dir):
    """A constant image must map to -mean/std, proving the statistics applied."""
    from PIL import Image

    grey = Image.new("RGB", (64, 64), color=(0, 0, 0))
    tensor = build_transform()(grey)

    expected = torch.tensor([-m / s for m, s in zip(IMAGENET_MEAN, IMAGENET_STD)]).view(
        3, 1, 1
    )
    assert torch.allclose(tensor, expected.expand_as(tensor), atol=1e-5)


def test_non_square_input_is_accepted(raw_dir):
    from PIL import Image

    tall = Image.new("RGB", (40, 160), color=(255, 255, 255))
    assert build_transform()(tall).shape == (3, IMAGE_SIZE, IMAGE_SIZE)


# --- Augmentation ---------------------------------------------------------


def test_augmented_output_has_the_same_shape(raw_dir):
    tensor = build_train_transform()(_sample(raw_dir))
    assert tensor.shape == (3, IMAGE_SIZE, IMAGE_SIZE)


def test_augmentation_actually_varies(raw_dir):
    """Without variation there is no regularisation."""
    image = _sample(raw_dir)
    transform = build_train_transform()
    torch.manual_seed(0)
    first = transform(image)
    torch.manual_seed(1)
    second = transform(image)
    assert not torch.equal(first, second)


def test_augmentation_is_reproducible_under_a_seed(raw_dir):
    image = _sample(raw_dir)
    transform = build_train_transform()
    torch.manual_seed(7)
    first = transform(image)
    torch.manual_seed(7)
    second = transform(image)
    assert torch.equal(first, second)


def test_training_pipeline_reuses_the_fixed_preprocessing(raw_dir):
    """Both pipelines must share one definition of resize and normalisation.

    Restating those steps inside the augmentation module would let the training
    and evaluation paths drift apart without any test noticing.
    """
    evaluation = [type(t).__name__ for t in build_transform().transforms]
    training = [type(t).__name__ for t in build_train_transform().transforms]

    assert "RandomAffine" in training
    assert [step for step in training if step != "RandomAffine"] == evaluation


def test_evaluation_transform_carries_no_randomness(raw_dir):
    """Regression guard: augmentation must never leak into evaluation."""
    image = _sample(raw_dir)
    transform = build_transform()
    torch.manual_seed(0)
    first = transform(image)
    torch.manual_seed(999)
    second = transform(image)
    assert torch.equal(first, second)
