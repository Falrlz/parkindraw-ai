"""Unit tests for clinical metrics computation module."""

import pytest

from src.evaluation.metrics import compute_metrics


def test_compute_metrics_perfect_predictions():
    """Verify perfect predictions yield 1.0 across all metrics."""
    y_true = [0, 1, 0, 1, 0, 1]
    y_pred = [0, 1, 0, 1, 0, 1]
    y_probs = [0.05, 0.95, 0.10, 0.88, 0.02, 0.99]

    metrics = compute_metrics(y_true, y_pred, y_probs)

    assert metrics["accuracy"] == pytest.approx(1.0)
    assert metrics["precision"] == pytest.approx(1.0)
    assert metrics["recall"] == pytest.approx(1.0)
    assert metrics["f1_score"] == pytest.approx(1.0)
    assert metrics["roc_auc"] == pytest.approx(1.0)


def test_compute_metrics_mixed_predictions():
    """Verify standard binary evaluation scoring."""
    y_true = [0, 0, 1, 1]
    y_pred = [0, 1, 1, 0]
    y_probs = [0.2, 0.8, 0.7, 0.3]

    metrics = compute_metrics(y_true, y_pred, y_probs)

    # Accuracy: 2/4 = 0.5
    assert metrics["accuracy"] == pytest.approx(0.5)
    # Precision: 1 TP / (1 TP + 1 FP) = 0.5
    assert metrics["precision"] == pytest.approx(0.5)
    # Recall: 1 TP / (1 TP + 1 FN) = 0.5
    assert metrics["recall"] == pytest.approx(0.5)
    # F1: 0.5
    assert metrics["f1_score"] == pytest.approx(0.5)
    assert 0.0 <= metrics["roc_auc"] <= 1.0


def test_compute_metrics_no_probabilities():
    """Verify behavior when no probability estimates are supplied."""
    y_true = [0, 1, 0, 1]
    y_pred = [0, 1, 0, 1]

    metrics = compute_metrics(y_true, y_pred)

    assert metrics["accuracy"] == pytest.approx(1.0)
    assert metrics["roc_auc"] == pytest.approx(0.0)


def test_compute_metrics_single_class_edge_case():
    """Verify safe handling when only one class is present in y_true."""
    y_true = [1, 1, 1, 1]
    y_pred = [1, 1, 1, 1]
    y_probs = [0.9, 0.8, 0.7, 0.85]

    metrics = compute_metrics(y_true, y_pred, y_probs)

    assert metrics["accuracy"] == pytest.approx(1.0)
    assert metrics["roc_auc"] == pytest.approx(0.0)


def test_format_metrics():
    """Verify string formatting helper output."""
    from src.evaluation.metrics import format_metrics

    metrics = {
        "accuracy": 0.85,
        "precision": 0.80,
        "recall": 0.90,
        "f1_score": 0.847,
        "roc_auc": 0.88,
    }
    summary = format_metrics(metrics)
    assert "Acc: 0.8500" in summary
    assert "Recall: 0.9000" in summary
    assert "ROC-AUC: 0.8800" in summary


