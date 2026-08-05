"""Smoke test for the training pipeline.

Runs the whole loop end to end on the synthetic dataset with a tiny budget.
The point is to prove the pipeline is wired correctly -- data, augmentation,
frozen backbone, metrics, checkpointing -- not to reach any accuracy.
"""

import pandas as pd
import pytest
import torch

from parkindraw.data.splits import run_split
from parkindraw.models.resnet18 import trainable_parameters
from parkindraw.training.config import TrainingConfig
from parkindraw.training.trainer import (
    build_loaders,
    fold_manifests,
    load_head,
    set_seed,
    train_fold,
)

N_SPLITS = 3


@pytest.fixture
def splits_dir(raw_dir, tmp_path):
    output = tmp_path / "splits"
    run_split(raw_dir, output, n_splits=N_SPLITS)
    return output


@pytest.fixture
def config(raw_dir, splits_dir):
    # Pretrained weights are skipped implicitly: the model is built inside
    # train_fold, so keep the budget tiny instead.
    return TrainingConfig(
        drawing_type="spiral",
        fold=0,
        epochs=1,
        batch_size=4,
        raw_dir=str(raw_dir),
        splits_dir=str(splits_dir),
        device="cpu",
    )


# --- Fold wiring ----------------------------------------------------------


def test_fold_splits_are_disjoint(config):
    train, validation = fold_manifests(config)
    assert not set(train.subject_id) & set(validation.subject_id)


def test_fold_never_includes_holdout_subjects(config, splits_dir):
    holdout = pd.read_csv(splits_dir / "holdout.csv")
    locked = set(holdout.loc[holdout.partition == "holdout", "subject_id"])

    train, validation = fold_manifests(config)
    assert not locked & set(train.subject_id)
    assert not locked & set(validation.subject_id)


def test_only_the_requested_drawing_type_is_used(config):
    train, validation = fold_manifests(config)
    for frame in (train, validation):
        assert set(frame.drawing_type) == {config.drawing_type}


def test_augmentation_is_applied_to_training_only(config):
    """The validation loader must be deterministic across epochs."""
    train, validation = fold_manifests(config)
    train_loader, validation_loader = build_loaders(train, validation, config)

    first = next(iter(validation_loader))[0]
    second = next(iter(validation_loader))[0]
    assert torch.equal(first, second)

    set_seed(1)
    a = next(iter(train_loader))[0]
    set_seed(2)
    b = next(iter(train_loader))[0]
    assert not torch.equal(a, b)


# --- Training loop --------------------------------------------------------


def test_training_runs_end_to_end(config):
    result = train_fold(config)
    assert len(result.history) == config.epochs
    assert result.best_epoch == 1

    entry = result.history[0]
    assert entry["train_loss"] > 0
    assert entry["validation_loss"] > 0
    assert "roc_auc" in entry


def test_backbone_stays_frozen_through_training(config):
    """Phase 2 exit criterion, verified after real optimisation steps."""
    from parkindraw.models.resnet18 import build_model

    model = build_model(pretrained=False)
    before = {n: p.clone() for n, p in model.backbone.named_parameters()}

    train_fold(config)

    assert all(name.startswith("head") for name in trainable_parameters(model))
    assert all(torch.equal(before[n], p) for n, p in model.backbone.named_parameters())


def test_checkpoint_is_written_and_reloadable(config, tmp_path):
    checkpoint = tmp_path / "nested" / "head.pt"
    train_fold(config, checkpoint)

    assert checkpoint.is_file()
    model = load_head(checkpoint, device="cpu")
    assert model.head.out_features == 2


def test_same_seed_reproduces_the_run(config):
    first = train_fold(config)
    second = train_fold(config)
    assert first.history == second.history


def test_config_is_recorded_with_the_result(config):
    result = train_fold(config)
    assert result.config["seed"] == config.seed
    assert result.config["drawing_type"] == config.drawing_type
