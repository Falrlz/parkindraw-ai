"""Clinical classification metrics calculation for ParkinDraw screening models."""

import logging

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

logger = logging.getLogger(__name__)


def compute_metrics(
    y_true: np.ndarray | list[int],
    y_pred: np.ndarray | list[int],
    y_probs: np.ndarray | list[float] | None = None,
    ) -> dict[str, float]:

    """Calculate clinical classification metrics."""
    y_true_arr = np.asarray(y_true, dtype=int)
    y_pred_arr = np.asarray(y_pred, dtype=int)

    # Core classification scores
    acc = float(accuracy_score(y_true_arr, y_pred_arr))
    prec = float(precision_score(y_true_arr, y_pred_arr, zero_division=0))
    rec = float(recall_score(y_true_arr, y_pred_arr, zero_division=0))
    f1 = float(f1_score(y_true_arr, y_pred_arr, zero_division=0))

    # ROC-AUC calculation
    auc = 0.0
    if y_probs is not None and len(np.unique(y_true_arr)) > 1:
        try:
            auc = float(roc_auc_score(y_true_arr, np.asarray(y_probs, dtype=float)))
        except ValueError:
            auc = 0.0

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "roc_auc": auc,
    }


def format_metrics(
    metrics: dict[str, float],
    ) -> str:

    """Format evaluation metrics into a human-readable summary string."""
    return (
        f"Acc: {metrics.get('accuracy', 0.0):.4f} | "
        f"Prec: {metrics.get('precision', 0.0):.4f} | "
        f"Recall: {metrics.get('recall', 0.0):.4f} | "
        f"F1: {metrics.get('f1_score', 0.0):.4f} | "
        f"ROC-AUC: {metrics.get('roc_auc', 0.0):.4f}"
    )
