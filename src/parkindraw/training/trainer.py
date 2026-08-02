"""Training loop for one drawing type on one fold.

Deliberately small: the backbone is frozen, so the only thing being fitted is a
512x2 linear layer. What matters here is not sophistication but that every run
is reproducible, that the holdout is never touched, and that the best
checkpoint -- not the last -- is the one kept.

Device handling goes through `resolve_device`, so moving to a rented GPU is a
config change rather than a code change.
"""

import random
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader

from parkindraw.data.dataset import DrawingDataset, build_manifest, filter_drawing
from parkindraw.evaluation.metrics import subject_metrics
from parkindraw.models.resnet18 import build_model, resolve_device
from parkindraw.preprocessing.augmentation import build_train_transform
from parkindraw.preprocessing.transforms import build_transform


@dataclass
class TrainingConfig:
    """Every knob that changes a run. Recorded verbatim next to the results."""

    drawing_type: str = "spiral"
    fold: int = 0
    epochs: int = 30
    batch_size: int = 32
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    early_stopping_patience: int = 5
    seed: int = 42
    device: str = "auto"
    num_workers: int = 0
    raw_dir: str = "data/raw"
    splits_dir: str = "data/splits"


@dataclass
class TrainingResult:
    config: dict
    history: list[dict] = field(default_factory=list)
    best_epoch: int = 0
    best_metrics: dict = field(default_factory=dict)


def set_seed(seed: int) -> None:
    """Seed every source of randomness the run depends on."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def fold_manifests(config: TrainingConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split the manifest into the train and validation halves of one fold.

    The fold files list development subjects only, so the locked holdout is
    excluded by construction -- there is no code path here that could read it.
    """
    manifest = filter_drawing(build_manifest(config.raw_dir), config.drawing_type)
    fold = pd.read_csv(Path(config.splits_dir) / f"fold_{config.fold}.csv")
    assignment = dict(zip(fold["subject_id"], fold["split"]))

    side = manifest["subject_id"].map(assignment)
    return manifest[side == "train"], manifest[side == "validation"]


def build_loaders(
    train_manifest: pd.DataFrame,
    validation_manifest: pd.DataFrame,
    config: TrainingConfig,
) -> tuple[DataLoader, DataLoader]:
    """Create the loaders. Augmentation is applied to the training half only."""
    train_dataset = DrawingDataset(
        train_manifest, config.raw_dir, transform=build_train_transform()
    )
    validation_dataset = DrawingDataset(
        validation_manifest, config.raw_dir, transform=build_transform()
    )
    return (
        DataLoader(
            train_dataset,
            batch_size=config.batch_size,
            shuffle=True,
            num_workers=config.num_workers,
        ),
        DataLoader(
            validation_dataset,
            batch_size=config.batch_size,
            shuffle=False,
            num_workers=config.num_workers,
        ),
    )


def run_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    optimizer: torch.optim.Optimizer | None = None,
) -> float:
    """One pass over `loader`. Training when an optimizer is supplied."""
    training = optimizer is not None
    model.train(training)

    total_loss = 0.0
    total_samples = 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)

        with torch.set_grad_enabled(training):
            logits = model(images)
            loss = criterion(logits, labels)

        if training:
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        total_loss += float(loss.detach()) * len(labels)
        total_samples += len(labels)
    return total_loss / max(total_samples, 1)


def predict(model: nn.Module, loader: DataLoader, device: torch.device) -> np.ndarray:
    """Probability of the positive class for every image in `loader`."""
    model.eval()
    probabilities = []
    with torch.no_grad():
        for images, _ in loader:
            logits = model(images.to(device))
            probabilities.append(torch.softmax(logits, dim=1)[:, 1].cpu().numpy())
    return np.concatenate(probabilities) if probabilities else np.array([])


def train_fold(
    config: TrainingConfig,
    checkpoint_path: str | Path | None = None,
) -> TrainingResult:
    """Train one fold and return its history plus the best epoch's metrics."""
    set_seed(config.seed)
    device = resolve_device(config.device)

    train_manifest, validation_manifest = fold_manifests(config)
    train_loader, validation_loader = build_loaders(
        train_manifest, validation_manifest, config
    )

    model = build_model(device=device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        (p for p in model.parameters() if p.requires_grad),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )

    result = TrainingResult(config=asdict(config))
    best_score = -1.0
    epochs_without_gain = 0

    for epoch in range(1, config.epochs + 1):
        train_loss = run_epoch(model, train_loader, criterion, device, optimizer)
        validation_loss = run_epoch(model, validation_loader, criterion, device)

        probabilities = predict(model, validation_loader, device)
        metrics = subject_metrics(
            validation_manifest["subject_id"].tolist(),
            validation_manifest["label"].tolist(),
            probabilities,
        )
        result.history.append(
            {
                "epoch": epoch,
                "train_loss": round(train_loss, 4),
                "validation_loss": round(validation_loss, 4),
                **{k: v for k, v in metrics.items() if k != "confusion_matrix"},
            }
        )

        # Selection uses ROC-AUC when it exists; a degenerate validation split
        # falls back to accuracy so a smoke run still makes progress.
        score = (
            metrics["roc_auc"]
            if metrics["roc_auc"] is not None
            else metrics["accuracy"]
        )
        if score > best_score:
            best_score = score
            result.best_epoch = epoch
            result.best_metrics = metrics
            epochs_without_gain = 0
            if checkpoint_path is not None:
                Path(checkpoint_path).parent.mkdir(parents=True, exist_ok=True)
                torch.save(model.head.state_dict(), checkpoint_path)
        else:
            epochs_without_gain += 1
            if epochs_without_gain >= config.early_stopping_patience:
                break

    return result


def load_head(checkpoint_path: str | Path, device: str | torch.device = "cpu"):
    """Rebuild a model from a saved head.

    Only the head is stored: the backbone is frozen pretrained weights, so
    saving it again for every run would waste space without adding information.
    `map_location` keeps checkpoints written on a GPU readable on CPU.
    """
    device = resolve_device(device) if isinstance(device, str) else device
    model = build_model(device=device)
    model.head.load_state_dict(torch.load(checkpoint_path, map_location=device))
    return model
