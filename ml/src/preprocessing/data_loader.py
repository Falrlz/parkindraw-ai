"""PyTorch Dataset and DataLoader factory for drawing image feeding."""

from collections.abc import Callable
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset

from src.config.config import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_NUM_WORKERS,
    RAW_DATA_DIR,
)
from src.preprocessing.augmentation import augmentation
from src.preprocessing.transforms import load_image, transform


class DrawingDataset(Dataset):
    """PyTorch Dataset for on-the-fly loading and transformation of drawing images."""

    def __init__(
        self,
        manifest: pd.DataFrame,
        raw_dir: str | Path = RAW_DATA_DIR,
        transform: Callable | None = None,
        augmentation: Callable | None = None,
        ) -> None:

        base_dir = Path(raw_dir)
        self.image_paths: list[Path] = [base_dir / p for p in manifest["filepath"]]
        self.labels: list[int] = [int(lbl) for lbl in manifest["label"]]
        self.transform = transform
        self.augmentation = augmentation

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, int]:
        image = load_image(self.image_paths[idx])
        if self.augmentation is not None:
            image = self.augmentation(image)
        if self.transform is not None:
            image = self.transform(image)
        return image, self.labels[idx]


def create_train_val_loaders(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    raw_dir: str | Path = RAW_DATA_DIR,
    batch_size: int = DEFAULT_BATCH_SIZE,
    num_workers: int = DEFAULT_NUM_WORKERS,
    ) -> tuple[DataLoader, DataLoader]:

    """Build training (augmented) and validation (deterministic) DataLoaders."""
    train_dataset = DrawingDataset(
        manifest=train_df,
        raw_dir=raw_dir,
        augmentation=augmentation(),
        transform=transform(),
    )
    val_dataset = DrawingDataset(
        manifest=val_df,
        raw_dir=raw_dir,
        transform=transform(),
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
    )
    return train_loader, val_loader


def create_eval_loader(
    df: pd.DataFrame,
    raw_dir: str | Path = RAW_DATA_DIR,
    batch_size: int = DEFAULT_BATCH_SIZE,
    num_workers: int = DEFAULT_NUM_WORKERS,
    ) -> DataLoader:

    """Build evaluation/testing DataLoader with deterministic preprocessing."""
    dataset = DrawingDataset(
        manifest=df,
        raw_dir=raw_dir,
        transform=transform(),
    )
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
    )
