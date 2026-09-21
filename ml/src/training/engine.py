import copy
import time

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader

from src.evaluation.metrics import compute_metrics, format_metrics
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EarlyStopping:
    """Stop training early if validation loss fails to improve."""

    def __init__(
        self,
        patience: int = 5,
        min_delta: float = 0.0,
        ) -> None:

        """Initialize early stopping tracker with patience and minimum loss delta."""
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float("inf")
        self.best_weights: dict[str, torch.Tensor] | None = None

    def step(
        self,
        val_loss: float,
        model: nn.Module,
        ) -> bool:

        """Check validation loss improvement and save best model state snapshot."""
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.best_weights = copy.deepcopy(model.state_dict())
            self.counter = 0
            return False
        self.counter += 1
        return self.counter >= self.patience


def train_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    ) -> float:

    """Train model for one epoch and return average training loss."""
    model.train()
    running_loss, total = 0.0, 0

    for images, labels in dataloader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        loss = criterion(model(images), labels)
        loss.backward()
        optimizer.step()

        batch_size = images.size(0)
        running_loss += loss.item() * batch_size
        total += batch_size

    return running_loss / max(total, 1)


def validate_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    ) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:

    """Evaluate model without gradients and return loss, targets, predictions, and probabilities."""
    model.eval()
    running_loss, total = 0.0, 0
    targets, preds, probs = [], [], []

    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            logits = model(images)
            loss = criterion(logits, labels)

            batch_size = images.size(0)
            running_loss += loss.item() * batch_size
            total += batch_size

            batch_probs = torch.softmax(logits, dim=1)
            targets.extend(labels.cpu().tolist())
            preds.extend(torch.argmax(batch_probs, dim=1).cpu().tolist())
            probs.extend(batch_probs[:, 1].cpu().tolist())

    avg_loss = running_loss / max(total, 1)
    return avg_loss, np.array(targets, dtype=int), np.array(preds, dtype=int), np.array(probs, dtype=float)


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    epochs: int,
    device: torch.device,
    *,
    scheduler: torch.optim.lr_scheduler.LRScheduler | None = None,
    early_stopping_patience: int | None = None,
    ) -> tuple[nn.Module, dict[str, list[float]], float]:

    """Train model with metrics tracking, early stopping, and best weights restoration."""
    start_time = time.time()
    history: dict[str, list[float]] = {
        "train_loss": [], "val_loss": [], "val_accuracy": [],
        "val_precision": [], "val_recall": [], "val_f1_score": [],
        "val_roc_auc": [], "learning_rate": [],
    }

    stopper = EarlyStopping(patience=early_stopping_patience) if early_stopping_patience else None
    best_weights = copy.deepcopy(model.state_dict())
    best_loss = float("inf")

    for epoch in range(1, epochs + 1):
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, y_true, y_pred, y_probs = validate_epoch(model, val_loader, criterion, device)
        metrics = compute_metrics(y_true, y_pred, y_probs)
        lr = optimizer.param_groups[0]["lr"]

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_accuracy"].append(metrics["accuracy"])
        history["val_precision"].append(metrics["precision"])
        history["val_recall"].append(metrics["recall"])
        history["val_f1_score"].append(metrics["f1_score"])
        history["val_roc_auc"].append(metrics["roc_auc"])
        history["learning_rate"].append(lr)

        logger.info(
            "Epoch %02d/%02d [LR: %.6f] - Train: %.4f | Val: %.4f | %s",
            epoch, epochs, lr, train_loss, val_loss, format_metrics(metrics),
        )

        if scheduler is not None:
            scheduler.step(val_loss) if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau) else scheduler.step()

        if stopper:
            if stopper.step(val_loss, model):
                logger.info("Early stopping active at epoch %d/%d (best loss: %.4f).", epoch, epochs, stopper.best_loss)
                break
        elif val_loss < best_loss:
            best_loss = val_loss
            best_weights = copy.deepcopy(model.state_dict())

    best_snap = stopper.best_weights if (stopper and stopper.best_weights) else best_weights
    model.load_state_dict(best_snap)
    duration = time.time() - start_time
    logger.info("Training completed in %.2f seconds.", duration)

    return model, history, duration
