"""Tests for the subject-level metrics."""

import pytest

from parkindraw.evaluation.metrics import (
    DECISION_THRESHOLD,
    aggregate_by_subject,
    subject_metrics,
    summarise_folds,
)


def test_aggregation_averages_within_a_subject():
    subjects = aggregate_by_subject(["H01", "H01", "P01"], [0, 0, 1], [0.2, 0.4, 0.9])
    row = subjects.set_index("subject_id")
    assert len(subjects) == 2
    assert row.loc["H01", "probability"] == pytest.approx(0.3)
    assert row.loc["P01", "probability"] == pytest.approx(0.9)


def test_conflicting_labels_are_rejected():
    with pytest.raises(ValueError, match="more than one label"):
        aggregate_by_subject(["H01", "H01"], [0, 1], [0.1, 0.2])


def test_perfect_separation_scores_one():
    result = subject_metrics(["H01", "P01"], [0, 1], [0.1, 0.9])
    assert result["roc_auc"] == 1.0
    assert result["accuracy"] == 1.0


def test_inverted_predictions_score_zero_auc():
    result = subject_metrics(["H01", "P01"], [0, 1], [0.9, 0.1])
    assert result["roc_auc"] == 0.0


def test_single_class_yields_no_auc():
    """Happens in tiny smoke runs; must not raise or emit NaN."""
    result = subject_metrics(["H01", "H02"], [0, 0], [0.2, 0.3])
    assert result["roc_auc"] is None
    assert result["accuracy"] == 1.0


def test_metrics_are_computed_per_subject_not_per_image():
    """Four images of one subject must not outweigh a single-image subject."""
    many = subject_metrics(
        ["P01"] * 4 + ["H01"], [1, 1, 1, 1, 0], [0.9, 0.9, 0.9, 0.9, 0.1]
    )
    assert many["subjects"] == 2


def test_confusion_matrix_counts_are_consistent():
    result = subject_metrics(
        ["H01", "H02", "P01", "P02"], [0, 0, 1, 1], [0.1, 0.8, 0.9, 0.2]
    )
    matrix = result["confusion_matrix"]
    assert sum(matrix.values()) == result["subjects"]
    assert matrix["true_negative"] == 1
    assert matrix["false_positive"] == 1
    assert matrix["true_positive"] == 1
    assert matrix["false_negative"] == 1


def test_threshold_is_applied_and_reported():
    scores = ["H01", "P01"], [0, 1], [0.4, 0.6]
    lenient = subject_metrics(*scores, threshold=0.3)
    assert lenient["threshold"] == 0.3
    assert lenient["confusion_matrix"]["false_positive"] == 1
    assert subject_metrics(*scores)["threshold"] == DECISION_THRESHOLD


def test_fold_summary_reports_mean_and_spread():
    summary = summarise_folds([{"roc_auc": 0.9}, {"roc_auc": 0.7}])
    assert summary["mean"] == 0.8
    assert summary["std"] == pytest.approx(0.1)
    assert summary["values"] == [0.9, 0.7]


def test_fold_summary_skips_missing_values():
    summary = summarise_folds([{"roc_auc": 0.9}, {"roc_auc": None}])
    assert summary["mean"] == 0.9
    assert summary["values"] == [0.9]


def test_fold_summary_handles_no_usable_values():
    assert summarise_folds([{"roc_auc": None}])["mean"] is None
