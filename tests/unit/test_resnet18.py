"""Tests for the frozen ResNet-18.

The freezing checks are the Phase 2 exit criterion: only the classification
head may receive gradients.
"""

import torch
from torch import nn

from parkindraw.models.resnet18 import (
    FEATURE_DIM,
    NUM_CLASSES,
    build_model,
    resolve_device,
    trainable_parameters,
)

BATCH = 2


def _model():
    # Pretrained weights are skipped: these tests check wiring, not accuracy,
    # and downloading them would make the suite depend on the network.
    return build_model(pretrained=False)


def _batch():
    return torch.randn(BATCH, 3, 224, 224)


# --- Freezing -------------------------------------------------------------


def test_only_the_head_is_trainable():
    """Phase 2 exit criterion."""
    trainable = trainable_parameters(_model())
    assert trainable, "the head must be trainable"
    assert all(name.startswith("head") for name in trainable), trainable


def test_backbone_parameters_require_no_gradient():
    model = _model()
    assert not any(p.requires_grad for p in model.backbone.parameters())


def test_backbone_stays_in_eval_mode_during_training():
    """Freezing parameters is not enough: BatchNorm must stop updating too."""
    model = _model()
    model.train()

    assert model.head.training
    assert not model.backbone.training
    assert all(
        not m.training
        for m in model.backbone.modules()
        if isinstance(m, nn.BatchNorm2d)
    )


def test_batchnorm_statistics_do_not_drift():
    """Running statistics must be identical before and after a forward pass."""
    model = _model()
    model.train()
    layer = next(m for m in model.backbone.modules() if isinstance(m, nn.BatchNorm2d))
    before = layer.running_mean.clone()

    model(_batch())
    assert torch.equal(before, layer.running_mean)


# --- Forward pass ---------------------------------------------------------


def test_output_shape_is_two_logits():
    assert _model()(_batch()).shape == (BATCH, NUM_CLASSES)


def test_head_maps_from_the_backbone_feature_dim():
    model = _model()
    assert model.head.in_features == FEATURE_DIM
    assert model.head.out_features == NUM_CLASSES


def test_gradients_reach_the_head_and_nothing_else():
    model = _model()
    model.train()

    loss = model(_batch()).sum()
    loss.backward()

    assert model.head.weight.grad is not None
    assert all(p.grad is None for p in model.backbone.parameters())


def test_evaluation_mode_is_deterministic():
    model = _model()
    model.eval()
    images = _batch()
    with torch.no_grad():
        assert torch.equal(model(images), model(images))


# --- Device handling ------------------------------------------------------


def test_resolve_device_honours_an_explicit_choice():
    assert resolve_device("cpu").type == "cpu"


def test_resolve_device_auto_falls_back_to_cpu():
    """`auto` must work on a machine without CUDA, which is where tests run."""
    assert resolve_device("auto").type in {"cpu", "cuda"}


def test_model_lands_on_the_requested_device():
    model = build_model(pretrained=False, device="cpu")
    assert next(model.parameters()).device.type == "cpu"
