"""Quality gate: a split must never leak subjects across partitions."""

import json

import pandas as pd
import pytest

from parkindraw.data.dataset import build_manifest
from parkindraw.data.splits import (
    SplitError,
    build_clusters,
    build_folds,
    build_holdout,
    build_sessions,
    cluster_ids,
    hash_images,
    run_split,
    verify_no_leakage,
)

N_SPLITS = 3
SESSIONS_PER_SUBJECT = 4


@pytest.fixture
def clusters(raw_dir):
    """Duplicate-subject clusters, derived from the actual file contents."""
    manifest = build_manifest(raw_dir)
    return build_clusters(manifest, hash_images(manifest, raw_dir))


@pytest.fixture
def split_result(raw_dir, tmp_path):
    """Run the full split pipeline and return its artifacts."""
    output = tmp_path / "splits"
    summary = run_split(raw_dir, output, n_splits=N_SPLITS)
    return {
        "dir": output,
        "summary": summary,
        "holdout": pd.read_csv(output / "holdout.csv"),
        "folds": [pd.read_csv(output / f"fold_{i}.csv") for i in range(N_SPLITS)],
        "sessions": pd.read_csv(output / "sessions.csv"),
    }


def _subjects(frame, column, value):
    return set(frame.loc[frame[column] == value, "subject_id"])


# --- Primary quality gate -------------------------------------------------


def test_holdout_and_development_are_disjoint(split_result):
    holdout = split_result["holdout"]
    assert not (
        _subjects(holdout, "partition", "holdout")
        & _subjects(holdout, "partition", "development")
    )


def test_train_and_validation_are_disjoint(split_result):
    for number, fold in enumerate(split_result["folds"]):
        leaked = _subjects(fold, "split", "train") & _subjects(
            fold, "split", "validation"
        )
        assert not leaked, f"fold_{number} leaks subjects: {sorted(leaked)}"


def test_folds_never_touch_the_holdout(split_result):
    locked = _subjects(split_result["holdout"], "partition", "holdout")
    for number, fold in enumerate(split_result["folds"]):
        leaked = locked & set(fold.subject_id)
        assert not leaked, f"fold_{number} uses holdout subjects: {sorted(leaked)}"


def test_no_image_appears_in_two_partitions(raw_dir, split_result):
    """An image-level guarantee, not merely a subject-level one."""
    manifest = build_manifest(raw_dir)
    holdout = split_result["holdout"]
    locked = _subjects(holdout, "partition", "holdout")
    development = _subjects(holdout, "partition", "development")

    locked_images = set(manifest.loc[manifest.subject_id.isin(locked), "filepath"])
    development_images = set(
        manifest.loc[manifest.subject_id.isin(development), "filepath"]
    )
    assert not (locked_images & development_images)


# --- Completeness and consistency -----------------------------------------


def test_every_subject_receives_a_partition(raw_dir, split_result, total_subjects):
    holdout = split_result["holdout"]
    assert len(holdout) == total_subjects
    assert set(holdout.subject_id) == set(build_manifest(raw_dir).subject_id)
    assert set(holdout.partition) == {"development", "holdout"}


def test_every_development_subject_is_validated_exactly_once(split_result):
    development = _subjects(split_result["holdout"], "partition", "development")
    counts = (
        pd.concat(split_result["folds"])
        .query("split == 'validation'")
        .subject_id.value_counts()
    )
    assert set(counts.index) == development
    assert (counts == 1).all()


def test_both_classes_are_present_in_every_partition(split_result):
    holdout = split_result["holdout"]
    for partition in ("development", "holdout"):
        classes = set(holdout.loc[holdout.partition == partition, "class_name"])
        assert classes == {"Healthy", "Parkinson"}


# --- Application-matched sessions -----------------------------------------


def test_sessions_cover_holdout_subjects_only(split_result):
    locked = _subjects(split_result["holdout"], "partition", "holdout")
    sessions = split_result["sessions"]
    assert set(sessions.subject_id) == locked
    assert len(sessions) == len(locked) * SESSIONS_PER_SUBJECT


def test_each_session_uses_one_image_per_drawing_type(split_result):
    sessions = split_result["sessions"]
    assert sessions[["circle", "meander", "spiral"]].notna().all().all()
    assert sessions.session_id.is_unique


def test_the_circle_is_reused_across_four_sessions(split_result):
    """The dataset provides only one Circle per subject."""
    for _, group in split_result["sessions"].groupby("subject_id"):
        assert group.circle.nunique() == 1
        assert group.meander.nunique() == SESSIONS_PER_SUBJECT
        assert group.spiral.nunique() == SESSIONS_PER_SUBJECT


def test_a_session_uses_one_subject_for_all_three_drawings(raw_dir, split_result):
    manifest = build_manifest(raw_dir).set_index("filepath")
    for row in split_result["sessions"].itertuples():
        subjects = {
            manifest.loc[getattr(row, drawing), "subject_id"]
            for drawing in ("circle", "meander", "spiral")
        }
        assert subjects == {row.subject_id}


# --- Reproducibility ------------------------------------------------------


def test_the_same_seed_produces_an_identical_split(raw_dir, tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"
    run_split(raw_dir, first, seed=7)
    run_split(raw_dir, second, seed=7)
    for name in ("holdout.csv", "fold_0.csv", "sessions.csv"):
        assert (first / name).read_text() == (second / name).read_text()


def test_a_different_seed_produces_a_different_split(raw_dir, tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"
    run_split(raw_dir, first, seed=1)
    run_split(raw_dir, second, seed=99)
    assert (first / "holdout.csv").read_text() != (second / "holdout.csv").read_text()


def test_config_records_the_seed_and_sizes(split_result):
    config = json.loads((split_result["dir"] / "split_config.json").read_text())
    assert config["seed"] == 42
    assert config["n_splits"] == N_SPLITS
    assert (
        config["holdout_subjects"] + config["development_subjects"]
        == config["total_subjects"]
    )


def test_all_artifacts_are_written(split_result):
    expected = {
        "holdout.csv",
        "sessions.csv",
        "split_config.json",
        *(f"fold_{i}.csv" for i in range(N_SPLITS)),
    }
    assert {p.name for p in split_result["dir"].iterdir()} == expected


# --- Duplicate-image handling ---------------------------------------------


def test_clusters_are_discovered_from_file_contents(clusters, duplicate_cluster):
    """The cluster map is derived from hashes, never hand-maintained."""
    discovered = {
        tuple(sorted(s for s, own in clusters.items() if own == cluster_id))
        for cluster_id in set(clusters.values())
    }
    assert discovered == {duplicate_cluster}


def test_duplicate_subjects_stay_in_one_partition(split_result, clusters):
    """Subjects sharing identical images must land in the same partition."""
    holdout = split_result["holdout"]
    for cluster_id, group in holdout.groupby(
        cluster_ids(holdout["subject_id"], clusters)
    ):
        partitions = set(group["partition"])
        assert len(partitions) == 1, (
            f"Cluster {cluster_id} split across partitions: {partitions}"
        )


def test_duplicate_subjects_stay_in_one_fold(split_result, clusters):
    """Duplicate subjects in the dev set must share a train/validation side."""
    for number, fold in enumerate(split_result["folds"]):
        for cluster_id, group in fold.groupby(
            cluster_ids(fold["subject_id"], clusters)
        ):
            splits = set(group["split"])
            assert len(splits) == 1, (
                f"Fold {number}: cluster {cluster_id} split across: {splits}"
            )


def test_clusters_are_recorded_in_the_config(split_result, clusters):
    config = json.loads((split_result["dir"] / "split_config.json").read_text())
    recorded = {
        subject: cluster_id
        for cluster_id, members in config["duplicate_clusters"].items()
        for subject in members
    }
    assert recorded == dict(clusters)


# --- Internal guards ------------------------------------------------------


def test_verify_no_leakage_detects_a_violation(raw_dir, clusters):
    """The guard must genuinely fail when the holdout leaks into a fold."""
    manifest = build_manifest(raw_dir)
    hashes = hash_images(manifest, raw_dir)
    holdout = build_holdout(manifest, clusters)
    development = holdout.loc[holdout.partition == "development", "subject_id"]
    folds = build_folds(manifest, development, clusters, n_splits=N_SPLITS)

    locked = holdout.loc[holdout.partition == "holdout", "subject_id"].iloc[0]
    contaminated = folds[0].copy()
    contaminated.loc[len(contaminated)] = {
        "subject_id": locked,
        "class_name": "Healthy",
        "label": 0,
        "split": "train",
    }

    with pytest.raises(SplitError, match="Holdout subjects appear"):
        verify_no_leakage(manifest, hashes, holdout, [contaminated])


def test_verify_no_leakage_detects_a_missed_cluster(raw_dir):
    """Regression: an incomplete cluster map must still be caught.

    This is the failure that previously slipped through, because the guard
    validated against the same cluster map used to build the split.
    """
    manifest = build_manifest(raw_dir)
    hashes = hash_images(manifest, raw_dir)
    complete = build_clusters(manifest, hashes)
    partial = {s: own for s, own in complete.items() if own != "P01"}

    holdout = build_holdout(manifest, partial, seed=3)
    development = holdout.loc[holdout.partition == "development", "subject_id"]
    folds = build_folds(manifest, development, partial, n_splits=N_SPLITS, seed=3)

    with pytest.raises(SplitError, match="identical image"):
        verify_no_leakage(manifest, hashes, holdout, folds)


def test_build_sessions_rejects_a_subject_without_a_circle(raw_dir):
    manifest = build_manifest(raw_dir)
    subject = manifest.subject_id.iloc[0]
    without_circle = manifest.drop(
        manifest[
            (manifest.subject_id == subject) & (manifest.drawing_type == "circle")
        ].index
    )
    with pytest.raises(SplitError, match="exactly one circle"):
        build_sessions(without_circle, pd.Series([subject]))
