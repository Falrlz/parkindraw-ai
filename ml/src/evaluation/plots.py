from collections.abc import Sequence
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix


def plot_confusion_matrix(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    labels: tuple[str, str] = ("Healthy", "Parkinson"),
    title: str = "Confusion Matrix",
    save_path: str | Path | None = None,
    ) -> Path | None:

    """Plot confusion matrix visualization with counts and normalized percentages."""
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    cm_norm = cm.astype(float) / np.maximum(cm.sum(axis=1, keepdims=True), 1)

    fig, ax = plt.subplots(figsize=(5, 4.5), dpi=300)
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ax.set(
        xticks=[0, 1],
        yticks=[0, 1],
        xticklabels=labels,
        yticklabels=labels,
        ylabel="True Label",
        xlabel="Predicted Label",
        title=title,
    )

    thresh = cm.max() / 2.0
    for i in range(2):
        for j in range(2):
            text = f"{cm[i, j]}\n({cm_norm[i, j]:.1%})"
            color = "white" if cm[i, j] > thresh else "black"
            ax.text(j, i, text, ha="center", va="center", color=color, fontweight="bold")

    plt.tight_layout()
    if save_path:
        out = Path(save_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, bbox_inches="tight", dpi=300)
        plt.close(fig)
        return out

    plt.close(fig)
    return None


def plot_loss_accuracy(
    epochs: Sequence[int],
    train_loss: Sequence[float],
    val_loss: Sequence[float],
    val_accuracy: Sequence[float],
    title: str = "Training & Validation Performance",
    save_path: str | Path | None = None,
    ) -> Path | None:

    """Plot training vs validation loss and accuracy curves per epoch."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

    # Plot Loss (Train vs Val)
    ax1.plot(epochs, train_loss, label="Train Loss", color="#1f77b4", marker="o", markersize=3, linewidth=1.5)
    ax1.plot(epochs, val_loss, label="Val Loss", color="#ff7f0e", marker="s", markersize=3, linewidth=1.5)
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.set_title("Cross-Entropy Loss")
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend()

    # Plot Accuracy
    ax2.plot(epochs, val_accuracy, label="Val Accuracy", color="#2ca02c", marker="^", markersize=3, linewidth=1.5)
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy")
    ax2.set_title("Validation Accuracy")
    ax2.set_ylim([0.0, 1.05])
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend()

    fig.suptitle(title, fontsize=12, fontweight="bold", y=0.98)
    plt.tight_layout()

    if save_path:
        out = Path(save_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, bbox_inches="tight", dpi=300)
        plt.close(fig)
        return out

    plt.close(fig)
    return None


def plot_multi_confusion_matrices(
    modalities_data: dict[str, tuple[Sequence[int], Sequence[int]]],
    labels: tuple[str, str] = ("Healthy", "Parkinson"),
    title: str = "Holdout Test Set - Confusion Matrices",
    save_path: str | Path | None = None,
    ) -> Path | None:

    """Plot side-by-side confusion matrices for multiple drawing modalities."""
    n = len(modalities_data)
    fig, axes = plt.subplots(1, n, figsize=(4.8 * n, 4.2), dpi=300)
    if n == 1:
        axes = [axes]

    for ax, (modality, (y_true, y_pred)) in zip(axes, modalities_data.items(), strict=False):
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        cm_norm = cm.astype(float) / np.maximum(cm.sum(axis=1, keepdims=True), 1)

        im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

        ax.set(
            xticks=[0, 1],
            yticks=[0, 1],
            xticklabels=labels,
            yticklabels=labels,
            ylabel="True Label",
            xlabel="Predicted Label",
            title=f"{modality.capitalize()} (n={len(y_true)})",
        )

        thresh = cm.max() / 2.0
        for i in range(2):
            for j in range(2):
                text = f"{cm[i, j]}\n({cm_norm[i, j]:.1%})"
                color = "white" if cm[i, j] > thresh else "black"
                ax.text(j, i, text, ha="center", va="center", color=color, fontweight="bold")

    fig.suptitle(title, fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()

    if save_path:
        out = Path(save_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, bbox_inches="tight", dpi=300)
        plt.close(fig)
        return out

    plt.close(fig)
    return None
