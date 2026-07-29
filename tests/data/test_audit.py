"""Contract tests for committed NewHandPD metadata artifacts."""

import json
import re
from pathlib import Path

import pandas as pd

METADATA_DIR = Path("data/metadata")


def test_metadata_artifact_set_is_committed() -> None:
    expected = {
        "images.csv",
        "subjects.csv",
        "duplicate_groups.csv",
        "near_duplicate_candidates.csv",
        "audit_report.json",
    }
    assert expected <= {path.name for path in METADATA_DIR.iterdir()}


def test_images_manifest_integrity() -> None:
    images = pd.read_csv(METADATA_DIR / "images.csv")

    assert len(images) == 594
    assert {
        "filepath",
        "filename",
        "raw_filename",
        "raw_stem",
        "raw_subject_token",
        "class_name",
        "label",
        "drawing_type",
        "drawing_index",
        "raw_subject_id",
        "subject_id",
        "width",
        "height",
        "channels",
        "checksum_sha256",
        "perceptual_dhash",
        "file_size_bytes",
        "anomaly_flags",
        "duplicate_group_id",
    } <= set(images.columns)
    assert set(images["label"]) == {0, 1}
    assert set(images["drawing_type"]) == {"circle", "meander", "spiral"}
    assert images["checksum_sha256"].str.fullmatch(r"[0-9a-f]{64}").all()
    assert images["perceptual_dhash"].str.fullmatch(r"[0-9a-f]{16}").all()
    assert images["drawing_index"].between(1, 4).all()
    assert not images.duplicated(["subject_id", "drawing_type", "drawing_index"]).any()

    drawing_counts = images["drawing_type"].value_counts().to_dict()
    assert drawing_counts == {"meander": 264, "spiral": 264, "circle": 66}


def test_subject_manifest_integrity() -> None:
    subjects = pd.read_csv(METADATA_DIR / "subjects.csv")

    assert len(subjects) == 66
    assert (subjects["label"] == 0).sum() == 35
    assert (subjects["label"] == 1).sum() == 31
    assert (subjects["circle_count"] == 1).all()
    assert (subjects["meander_count"] == 4).all()
    assert (subjects["spiral_count"] == 4).all()
    assert (subjects["total_images"] == 9).all()


def test_exact_duplicate_manifest_integrity() -> None:
    duplicates = pd.read_csv(METADATA_DIR / "duplicate_groups.csv")

    assert duplicates["duplicate_group_id"].nunique() == 36
    assert len(duplicates) == 80
    assert (duplicates.groupby("duplicate_group_id").size() >= 2).all()


def test_near_duplicate_manifest_has_stable_schema() -> None:
    candidates = pd.read_csv(METADATA_DIR / "near_duplicate_candidates.csv")

    assert {
        "candidate_id",
        "filepath_a",
        "filepath_b",
        "subject_id_a",
        "subject_id_b",
        "class_name_a",
        "class_name_b",
        "drawing_type",
        "hamming_distance",
        "dhash_a",
        "dhash_b",
    } == set(candidates.columns)
    assert candidates["candidate_id"].is_unique


def test_audit_report_is_deterministic_and_passed() -> None:
    report = json.loads(
        (METADATA_DIR / "audit_report.json").read_text(encoding="utf-8")
    )

    assert "audit_timestamp" not in report
    assert report["status"] == "passed"
    assert report["validation_errors"] == []
    assert report["total_images"] == 594
    assert report["total_subjects"] == 66
    assert report["healthy_subjects"] == 35
    assert report["parkinson_subjects"] == 31
    assert report["exact_duplicate_groups_count"] == 36
    assert report["exact_duplicate_images_count"] == 80
    assert report["corrupted_images_count"] == 0
    assert report["invalid_metadata_files_count"] == 0
    assert re.fullmatch(
        r"[0-9a-f]{64}",
        report["dataset_fingerprint_sha256"],
    )
