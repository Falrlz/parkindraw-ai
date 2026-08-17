"""Tests for the metadata-only baseline."""

import json

import numpy as np
import pandas as pd
import pytest

from parkindraw.data.dataset import build_manifest
from parkindraw.data.splits import run_split
from parkindraw.evaluation.baseline import (
    FEATURES,
    BaselineError,
    development_subjects,
    diagnose,
    evaluate_fold,
    image_metadata,
    ink_fraction,
    load_folds,
    run_baseline,
)

N_SPLITS = 3


@pytest.fixture
def splits_dir(raw_dir, tmp_path):
    output = tmp_path / "splits"
    run_split(raw_dir, output, n_splits=N_SPLITS)
    return output


@pytest.fixture
def baseline(raw_dir, splits_dir, tmp_path):
    return run_baseline(
        raw_dir,
        splits_dir,
        tmp_path / "report.json",
        n_splits=N_SPLITS,
    )


# --- Feature extraction ------------------------------------------------------


def test_metadata_covers_every_image(raw_dir, total_images):
    features = image_metadata(build_manifest(raw_dir), raw_dir)
    assert len(features) == total_images
    assert set(FEATURES) <= set(features.columns)
    assert features[list(FEATURES)].notna().all().all()


def test_aspect_ratio_matches_dimensions(raw_dir):
    features = image_metadata(build_manifest(raw_dir), raw_dir)
    expected = features["width"] / features["height"]
    assert np.allclose(features["aspect_ratio"], expected)


def test_features_carry_no_clinical_information(raw_dir):
    """The baseline must describe the file, never the stroke."""
    features = image_metadata(build_manifest(raw_dir), raw_dir)
    assert set(FEATURES).isdisjoint({"label", "class_name", "subject_id"})
    assert "ink" not in " ".join(features.columns)


# --- Subject-level aggregation ------------------------------------------------


def test_baseline_and_model_share_one_aggregation():
    """Both scores are only comparable while aggregated identically."""
    from parkindraw.evaluation import baseline, metrics

    assert baseline.aggregate_by_subject is metrics.aggregate_by_subject


# The aggregation itself is covered by tests/unit/test_metrics.py; duplicating
# those assertions here would mirror the duplication just removed from the code.


# --- Evaluation -------------------------------------------------------------


def test_single_class_validation_is_rejected(raw_dir):
    features = image_metadata(build_manifest(raw_dir), raw_dir)
    healthy_only = features[features["label"] == 0]
    with pytest.raises(BaselineError, match="single class"):
        evaluate_fold(features, healthy_only)


def test_missing_fold_file_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError, match="Fold manifest not found"):
        load_folds(tmp_path, N_SPLITS)


def test_baseline_reports_every_drawing_type(baseline):
    assert set(baseline["results"]) == {"circle", "meander", "spiral"}


def test_auc_is_within_range(baseline):
    for drawing_type, result in baseline["results"].items():
        assert 0.0 <= result["mean_auc"] <= 1.0, drawing_type
        assert len(result["fold_auc"]) == N_SPLITS
        assert all(0.0 <= score <= 1.0 for score in result["fold_auc"])


def test_highest_matches_the_per_drawing_results(baseline):
    assert baseline["highest_mean_auc"] == max(
        result["mean_auc"] for result in baseline["results"].values()
    )


def test_folds_never_contain_holdout_subjects(splits_dir):
    master = pd.read_csv(splits_dir / "master_manifest.csv")
    locked = set(master.loc[master.partition == "holdout", "subject_id"])
    development = set(master.loc[master.partition == "development", "subject_id"])

    folds = load_folds(splits_dir, N_SPLITS)
    for number, fold in enumerate(folds):
        assert not locked & set(fold.subject_id), f"fold_{number} touches the holdout"
        assert set(fold.subject_id) <= development


def test_reported_counts_exclude_the_holdout(raw_dir, splits_dir, baseline):
    """Regression: counts once described the whole manifest, holdout included."""
    master = pd.read_csv(splits_dir / "master_manifest.csv")
    development = set(master.loc[master.partition == "development", "subject_id"])

    manifest = build_manifest(raw_dir)
    manifest = manifest[manifest.subject_id.isin(development)]

    for drawing_type, result in baseline["results"].items():
        expected = manifest[manifest.drawing_type == drawing_type]
        assert result["subjects"] == expected.subject_id.nunique(), drawing_type
        assert result["images"] == len(expected), drawing_type
        assert result["subjects"] == len(development)


# --- Diagnostics ----------------------------------------------------------


def test_diagnostics_cover_every_drawing_type(baseline):
    assert set(baseline["diagnostics"]) == {"circle", "meander", "spiral"}


def test_correlations_are_valid(baseline):
    """A constant feature yields None, never NaN -- NaN is not valid JSON."""
    keys = ("file_size_vs_ink", "file_size_vs_pixel_count", "ink_vs_label")
    for drawing_type, entry in baseline["diagnostics"].items():
        for key in keys:
            value = entry[key]
            assert value is None or -1.0 <= value <= 1.0, f"{drawing_type}.{key}"


def test_ink_fraction_is_a_proportion(raw_dir):
    manifest = build_manifest(raw_dir)
    values = [ink_fraction(p, raw_dir) for p in manifest.filepath.head(5)]
    assert all(0.0 <= v <= 1.0 for v in values)


def test_diagnostics_separate_the_two_explanations(raw_dir, splits_dir):
    """Both routes must be reported, so a high baseline is never ambiguous."""
    folds = load_folds(splits_dir, N_SPLITS)
    manifest = build_manifest(raw_dir)
    development = manifest[manifest.subject_id.isin(development_subjects(folds))]
    report = diagnose(image_metadata(development, raw_dir), raw_dir)

    for entry in report.values():
        assert set(entry["mean_file_size_kb"]) == {"Healthy", "Parkinson"}
        assert set(entry["mean_ink"]) == {"Healthy", "Parkinson"}


# --- Reproducibility ------------------------------------------------------


def test_same_seed_reproduces_the_baseline(raw_dir, splits_dir, tmp_path):
    first = run_baseline(raw_dir, splits_dir, None, n_splits=N_SPLITS, seed=11)
    second = run_baseline(raw_dir, splits_dir, None, n_splits=N_SPLITS, seed=11)
    assert first["results"] == second["results"]


def test_report_is_written(raw_dir, splits_dir, tmp_path):
    output = tmp_path / "nested" / "report.json"
    summary = run_baseline(raw_dir, splits_dir, output, n_splits=N_SPLITS)

    assert output.is_file()
    assert json.loads(output.read_text()) == summary


def test_report_can_be_skipped(raw_dir, splits_dir):
    assert run_baseline(raw_dir, splits_dir, None, n_splits=N_SPLITS)["results"]
