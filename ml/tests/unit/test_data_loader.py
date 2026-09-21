"""Tests for Dataset and DataLoader factory functions in src.preprocessing.data_loader."""

import torch
from torch.utils.data import DataLoader

from src.data.manifest import build_manifest
from src.preprocessing.data_loader import (
    DrawingDataset,
    create_eval_loader,
    create_train_val_loaders,
)


def test_create_train_val_loaders_returns_valid_dataloaders(raw_dir):
    manifest = build_manifest(raw_dir)
    train_df = manifest.iloc[:10]
    val_df = manifest.iloc[10:15]

    train_loader, val_loader = create_train_val_loaders(
        train_df=train_df,
        val_df=val_df,
        raw_dir=raw_dir,
        batch_size=4,
        num_workers=0,
    )

    assert isinstance(train_loader, DataLoader)
    assert isinstance(val_loader, DataLoader)
    assert isinstance(train_loader.dataset, DrawingDataset)
    assert isinstance(val_loader.dataset, DrawingDataset)
    assert len(train_loader.dataset) == 10
    assert len(val_loader.dataset) == 5
    assert train_loader.batch_size == 4
    assert val_loader.batch_size == 4


def test_create_train_val_loaders_batch_shapes(raw_dir):
    manifest = build_manifest(raw_dir)
    train_df = manifest.iloc[:4]
    val_df = manifest.iloc[4:6]

    train_loader, val_loader = create_train_val_loaders(
        train_df=train_df,
        val_df=val_df,
        raw_dir=raw_dir,
        batch_size=2,
    )

    train_images, train_labels = next(iter(train_loader))
    assert train_images.shape == (2, 3, 224, 224)
    assert train_labels.shape == (2,)
    assert train_images.dtype == torch.float32

    val_images, val_labels = next(iter(val_loader))
    assert val_images.shape == (2, 3, 224, 224)
    assert val_labels.shape == (2,)
    assert val_images.dtype == torch.float32


def test_create_eval_loader(raw_dir):
    manifest = build_manifest(raw_dir)
    eval_df = manifest.iloc[:6]

    eval_loader = create_eval_loader(
        df=eval_df,
        raw_dir=raw_dir,
        batch_size=3,
        num_workers=0,
    )

    assert isinstance(eval_loader, DataLoader)
    assert isinstance(eval_loader.dataset, DrawingDataset)
    assert len(eval_loader.dataset) == 6
    assert eval_loader.batch_size == 3

    images, labels = next(iter(eval_loader))
    assert images.shape == (3, 3, 224, 224)
    assert labels.shape == (3,)
    assert images.dtype == torch.float32
