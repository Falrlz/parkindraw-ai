"""Integration tests for the configurable audit pipeline."""

import json
import shutil
from pathlib import Path

import pandas as pd
import yaml
from PIL import Image

from parkindraw.data.audit import (
    AuditConfig,
    ExpectedDataset,
    NearDuplicateConfig,
    main,
    run_data_audit,
)


def save_image(
    root: Path,
    folder: str,
    filename: str,
    *,
    color: str = "white",
) -> Path:
    path = root / folder / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (40, 30), color=color).save(path)
    return path


def build_small_dataset(raw_dir: Path) -> None:
    first = save_image(raw_dir, "HealthyCircle", "circA-H1.jpg")
    duplicate = raw_dir / "HealthyMeander" / "mea1-H1.jpg"
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(first, duplicate)
    save_image(
        raw_dir,
        "PatientSpiral",
        "sp1-P1.jpg",
        color="black",
    )


def artifact_bytes(output_dir: Path) -> dict[str, bytes]:
    return {
        path.name: path.read_bytes()
        for path in sorted(output_dir.iterdir())
        if path.is_file()
    }


def test_audit_writes_complete_deterministic_artifact_set(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "raw"
    output_a = tmp_path / "metadata-a"
    output_b = tmp_path / "metadata-b"
    build_small_dataset(raw_dir)

    report_a = run_data_audit(raw_dir, output_a)
    report_b = run_data_audit(raw_dir, output_b)

    assert report_a == report_b
    assert report_a["status"] == "passed"
    assert report_a["total_images"] == 3
    assert report_a["total_subjects"] == 2
    assert report_a["exact_duplicate_groups_count"] == 1
    assert report_a["exact_duplicate_images_count"] == 2
    assert artifact_bytes(output_a) == artifact_bytes(output_b)
    assert set(artifact_bytes(output_a)) == {
        "audit_report.json",
        "duplicate_groups.csv",
        "images.csv",
        "near_duplicate_candidates.csv",
        "subjects.csv",
    }

    images = pd.read_csv(output_a / "images.csv")
    assert len(images) == 3
    assert "perceptual_dhash" in images.columns

    duplicates = pd.read_csv(output_a / "duplicate_groups.csv")
    assert len(duplicates) == 2


def test_corrupt_and_malformed_files_are_reported_separately(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "raw"
    output_dir = tmp_path / "metadata"
    save_image(raw_dir, "HealthyCircle", "circA-H1.png")

    truncated = save_image(raw_dir, "HealthyCircle", "circA-H2.png")
    truncated.write_bytes(truncated.read_bytes()[:100])
    save_image(raw_dir, "HealthyCircle", "unexpected-H3.png")

    report = run_data_audit(raw_dir, output_dir)

    assert report["status"] == "failed"
    assert report["total_images"] == 1
    assert report["corrupted_images_count"] == 1
    assert report["invalid_metadata_files_count"] == 1
    assert report["unreadable_images"][0]["filepath"].endswith("circA-H2.png")
    assert report["invalid_metadata_files"][0]["filepath"].endswith("unexpected-H3.png")


def test_near_duplicate_hook_reports_non_identical_visual_candidates(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "raw"
    output_dir = tmp_path / "metadata"
    save_image(raw_dir, "HealthySpiral", "sp1-H1.png", color="white")
    save_image(raw_dir, "HealthySpiral", "sp1-H2.png", color="gray")
    config = AuditConfig.for_paths(
        raw_dir,
        output_dir,
        near_duplicate=NearDuplicateConfig(max_hamming_distance=0),
    )

    report = run_data_audit(config=config)

    assert report["exact_duplicate_images_count"] == 0
    assert report["near_duplicate_analysis"]["candidate_pairs_count"] == 1
    candidates = pd.read_csv(output_dir / "near_duplicate_candidates.csv")
    assert len(candidates) == 1
    assert candidates.loc[0, "hamming_distance"] == 0


def test_cli_honors_config_extensions_artifacts_and_expected_counts(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "raw"
    output_dir = tmp_path / "output"
    save_image(raw_dir, "HealthyCircle", "circA-H1.bmp")
    config_path = tmp_path / "audit.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "project_root": ".",
                "raw_data_dir": "raw",
                "metadata_output_dir": "ignored-by-override",
                "supported_extensions": [".bmp"],
                "artifacts": {
                    "images_csv": "custom-images.csv",
                    "subjects_csv": "custom-subjects.csv",
                    "duplicate_groups_csv": "custom-duplicates.csv",
                    "near_duplicate_candidates_csv": "custom-near.csv",
                    "audit_report_json": "custom-report.json",
                },
                "expected_dataset": {
                    "total_images": 1,
                    "total_subjects": 1,
                    "healthy_subjects": 1,
                    "parkinson_subjects": 0,
                },
                "near_duplicate": {"enabled": False},
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--config",
            str(config_path),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    assert (output_dir / "custom-images.csv").exists()
    report = json.loads((output_dir / "custom-report.json").read_text())
    assert report["total_images"] == 1
    assert report["near_duplicate_analysis"]["enabled"] is False


def test_expected_count_mismatch_marks_report_failed(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    output_dir = tmp_path / "metadata"
    save_image(raw_dir, "HealthyCircle", "circA-H1.png")
    config = AuditConfig.for_paths(
        raw_dir,
        output_dir,
        expected=ExpectedDataset(total_images=2),
    )

    report = run_data_audit(config=config)

    assert report["status"] == "failed"
    assert report["validation_errors"] == ["total_images: expected 2, found 1"]
