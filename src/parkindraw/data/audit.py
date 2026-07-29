"""Deterministic and configurable dataset audit for NewHandPD."""

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from parkindraw.data.metadata import (
    ImageValidationError,
    MetadataParseError,
    parse_newhandpd_file,
)

DEFAULT_ARTIFACTS = {
    "images_csv": "images.csv",
    "subjects_csv": "subjects.csv",
    "duplicate_groups_csv": "duplicate_groups.csv",
    "near_duplicate_candidates_csv": "near_duplicate_candidates.csv",
    "audit_report_json": "audit_report.json",
}

IMAGE_COLUMNS = [
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
]

DUPLICATE_COLUMNS = [
    "duplicate_group_id",
    "filepath",
    "subject_id",
    "class_name",
    "drawing_type",
    "drawing_index",
    "checksum_sha256",
    "anomaly_flags",
]

NEAR_DUPLICATE_COLUMNS = [
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
]

SUBJECT_COLUMNS = [
    "subject_id",
    "class_name",
    "label",
    "circle_count",
    "meander_count",
    "spiral_count",
    "total_images",
    "has_anomalies",
]


class AuditConfigurationError(ValueError):
    """Raised when an audit configuration is incomplete or unsafe."""


@dataclass(frozen=True)
class NearDuplicateConfig:
    enabled: bool = True
    hash_size: int = 8
    max_hamming_distance: int = 2
    same_drawing_type_only: bool = True
    max_reported_candidates: int = 5_000

    def __post_init__(self) -> None:
        if self.hash_size < 4 or self.hash_size > 32:
            raise AuditConfigurationError("near_duplicate.hash_size must be 4..32")
        max_bits = self.hash_size * self.hash_size
        if not 0 <= self.max_hamming_distance <= max_bits:
            raise AuditConfigurationError(
                f"near_duplicate.max_hamming_distance must be 0..{max_bits}"
            )
        if self.max_reported_candidates < 1:
            raise AuditConfigurationError(
                "near_duplicate.max_reported_candidates must be positive"
            )


@dataclass(frozen=True)
class ExpectedDataset:
    total_images: int | None = None
    total_subjects: int | None = None
    healthy_subjects: int | None = None
    parkinson_subjects: int | None = None


@dataclass(frozen=True)
class AuditConfig:
    raw_data_dir: Path
    metadata_output_dir: Path
    supported_extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png")
    artifacts: dict[str, str] = field(default_factory=lambda: DEFAULT_ARTIFACTS.copy())
    expected: ExpectedDataset = field(default_factory=ExpectedDataset)
    near_duplicate: NearDuplicateConfig = field(default_factory=NearDuplicateConfig)

    def __post_init__(self) -> None:
        if not self.supported_extensions:
            raise AuditConfigurationError("supported_extensions cannot be empty")

        missing = set(DEFAULT_ARTIFACTS) - set(self.artifacts)
        if missing:
            raise AuditConfigurationError(
                f"Missing artifact names: {', '.join(sorted(missing))}"
            )

        artifact_values = list(self.artifacts.values())
        if len(artifact_values) != len(set(artifact_values)):
            raise AuditConfigurationError("Artifact filenames must be unique")

        for filename in artifact_values:
            path = Path(filename)
            if path.is_absolute() or path.name != filename:
                raise AuditConfigurationError(
                    f"Artifact must be a filename, not a path: {filename!r}"
                )

    @classmethod
    def for_paths(
        cls,
        raw_data_dir: str | Path,
        metadata_output_dir: str | Path,
        **kwargs: Any,
    ) -> "AuditConfig":
        """Build a config for programmatic use and synthetic tests."""
        return cls(
            raw_data_dir=Path(raw_data_dir),
            metadata_output_dir=Path(metadata_output_dir),
            **kwargs,
        )


def _positive_optional_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AuditConfigurationError(f"{field_name} must be a non-negative integer")
    return value


def load_audit_config(
    config_path: str | Path,
    *,
    raw_dir_override: str | Path | None = None,
    output_dir_override: str | Path | None = None,
    near_duplicates_override: bool | None = None,
) -> AuditConfig:
    """Load and validate a YAML audit configuration."""
    path = Path(config_path).resolve()
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except OSError as error:
        raise AuditConfigurationError(f"Cannot read config {path}: {error}") from error
    except yaml.YAMLError as error:
        raise AuditConfigurationError(f"Invalid YAML in {path}: {error}") from error

    if not isinstance(payload, dict):
        raise AuditConfigurationError("Audit config root must be a mapping")

    project_root_value = payload.get("project_root", "../..")
    project_root = (path.parent / str(project_root_value)).resolve()

    def resolve_project_path(value: Any, field_name: str) -> Path:
        if not isinstance(value, str) or not value.strip():
            raise AuditConfigurationError(f"{field_name} must be a non-empty string")
        candidate = Path(value)
        return (
            candidate.resolve() if candidate.is_absolute() else project_root / candidate
        )

    raw_value = (
        str(raw_dir_override)
        if raw_dir_override is not None
        else payload.get("raw_data_dir")
    )
    output_value = (
        str(output_dir_override)
        if output_dir_override is not None
        else payload.get("metadata_output_dir")
    )
    raw_data_dir = resolve_project_path(raw_value, "raw_data_dir")
    metadata_output_dir = resolve_project_path(
        output_value,
        "metadata_output_dir",
    )

    extensions_payload = payload.get(
        "supported_extensions",
        [".jpg", ".jpeg", ".png"],
    )
    if not isinstance(extensions_payload, list) or not all(
        isinstance(item, str) for item in extensions_payload
    ):
        raise AuditConfigurationError("supported_extensions must be a list of strings")
    supported_extensions = tuple(
        sorted(
            {
                extension.lower()
                if extension.startswith(".")
                else f".{extension.lower()}"
                for extension in extensions_payload
            }
        )
    )

    artifacts_payload = payload.get("artifacts", {})
    if not isinstance(artifacts_payload, dict):
        raise AuditConfigurationError("artifacts must be a mapping")
    artifacts = {
        key: str(artifacts_payload.get(key, default))
        for key, default in DEFAULT_ARTIFACTS.items()
    }

    expected_payload = payload.get("expected_dataset", {})
    if not isinstance(expected_payload, dict):
        raise AuditConfigurationError("expected_dataset must be a mapping")
    expected = ExpectedDataset(
        total_images=_positive_optional_int(
            expected_payload.get("total_images"),
            "expected_dataset.total_images",
        ),
        total_subjects=_positive_optional_int(
            expected_payload.get("total_subjects"),
            "expected_dataset.total_subjects",
        ),
        healthy_subjects=_positive_optional_int(
            expected_payload.get("healthy_subjects"),
            "expected_dataset.healthy_subjects",
        ),
        parkinson_subjects=_positive_optional_int(
            expected_payload.get("parkinson_subjects"),
            "expected_dataset.parkinson_subjects",
        ),
    )

    near_payload = payload.get("near_duplicate", {})
    if not isinstance(near_payload, dict):
        raise AuditConfigurationError("near_duplicate must be a mapping")
    near_enabled = (
        bool(near_duplicates_override)
        if near_duplicates_override is not None
        else bool(near_payload.get("enabled", True))
    )
    near_duplicate = NearDuplicateConfig(
        enabled=near_enabled,
        hash_size=int(near_payload.get("hash_size", 8)),
        max_hamming_distance=int(near_payload.get("max_hamming_distance", 2)),
        same_drawing_type_only=bool(near_payload.get("same_drawing_type_only", True)),
        max_reported_candidates=int(near_payload.get("max_reported_candidates", 5_000)),
    )

    return AuditConfig(
        raw_data_dir=raw_data_dir,
        metadata_output_dir=metadata_output_dir,
        supported_extensions=supported_extensions,
        artifacts=artifacts,
        expected=expected,
        near_duplicate=near_duplicate,
    )


def _relative_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def _discover_images(config: AuditConfig) -> list[Path]:
    raw_dir = config.raw_data_dir
    if not raw_dir.is_dir():
        raise FileNotFoundError(f"Raw dataset directory does not exist: {raw_dir}")
    return sorted(
        (
            path
            for path in raw_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in config.supported_extensions
        ),
        key=lambda path: path.relative_to(raw_dir).as_posix().casefold(),
    )


def _assign_exact_duplicates(
    records: list[dict],
) -> tuple[list[dict], int]:
    hash_groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        hash_groups[record["checksum_sha256"]].append(record)

    duplicate_rows: list[dict] = []
    duplicate_group_count = 0
    for checksum in sorted(hash_groups):
        group = sorted(hash_groups[checksum], key=lambda row: row["filepath"])
        if len(group) < 2:
            continue

        duplicate_group_count += 1
        duplicate_id = f"dup_{duplicate_group_count:03d}"
        for record in group:
            record["duplicate_group_id"] = duplicate_id
            duplicate_rows.append(
                {
                    "duplicate_group_id": duplicate_id,
                    "filepath": record["filepath"],
                    "subject_id": record["subject_id"],
                    "class_name": record["class_name"],
                    "drawing_type": record["drawing_type"],
                    "drawing_index": record["drawing_index"],
                    "checksum_sha256": checksum,
                    "anomaly_flags": record["anomaly_flags"],
                }
            )

    for record in records:
        record.setdefault("duplicate_group_id", "")

    return duplicate_rows, duplicate_group_count


def _hamming_distance(left_hash: str, right_hash: str) -> int:
    return (int(left_hash, 16) ^ int(right_hash, 16)).bit_count()


def _find_near_duplicates(
    records: list[dict],
    config: NearDuplicateConfig,
) -> tuple[list[dict], int, bool]:
    if not config.enabled:
        return [], 0, False

    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        group_key = record["drawing_type"] if config.same_drawing_type_only else "all"
        groups[group_key].append(record)

    candidates: list[dict] = []
    total_candidates = 0
    for group_key in sorted(groups):
        group = sorted(groups[group_key], key=lambda row: row["filepath"])
        for left, right in combinations(group, 2):
            if left["checksum_sha256"] == right["checksum_sha256"]:
                continue
            distance = _hamming_distance(
                left["perceptual_dhash"],
                right["perceptual_dhash"],
            )
            if distance > config.max_hamming_distance:
                continue

            total_candidates += 1
            if len(candidates) >= config.max_reported_candidates:
                continue
            candidates.append(
                {
                    "candidate_id": f"near_{total_candidates:04d}",
                    "filepath_a": left["filepath"],
                    "filepath_b": right["filepath"],
                    "subject_id_a": left["subject_id"],
                    "subject_id_b": right["subject_id"],
                    "class_name_a": left["class_name"],
                    "class_name_b": right["class_name"],
                    "drawing_type": (
                        left["drawing_type"]
                        if config.same_drawing_type_only
                        else f"{left['drawing_type']}|{right['drawing_type']}"
                    ),
                    "hamming_distance": distance,
                    "dhash_a": left["perceptual_dhash"],
                    "dhash_b": right["perceptual_dhash"],
                }
            )

    return (
        candidates,
        total_candidates,
        total_candidates > config.max_reported_candidates,
    )


def _build_subjects_dataframe(images: pd.DataFrame) -> pd.DataFrame:
    subject_rows: list[dict] = []
    if images.empty:
        return pd.DataFrame(columns=SUBJECT_COLUMNS)

    for (subject_id, class_name, label), group in images.groupby(
        ["subject_id", "class_name", "label"],
        sort=True,
    ):
        subject_rows.append(
            {
                "subject_id": subject_id,
                "class_name": class_name,
                "label": int(label),
                "circle_count": int((group["drawing_type"] == "circle").sum()),
                "meander_count": int((group["drawing_type"] == "meander").sum()),
                "spiral_count": int((group["drawing_type"] == "spiral").sum()),
                "total_images": len(group),
                "has_anomalies": bool((group["anomaly_flags"] != "none").any()),
            }
        )
    return pd.DataFrame(subject_rows, columns=SUBJECT_COLUMNS)


def _dataset_fingerprint(records: list[dict]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(record["filepath"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(record["checksum_sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _expected_count_errors(
    expected: ExpectedDataset,
    *,
    total_images: int,
    total_subjects: int,
    healthy_subjects: int,
    parkinson_subjects: int,
) -> list[str]:
    actual = {
        "total_images": total_images,
        "total_subjects": total_subjects,
        "healthy_subjects": healthy_subjects,
        "parkinson_subjects": parkinson_subjects,
    }
    errors: list[str] = []
    for field_name, actual_value in actual.items():
        expected_value = getattr(expected, field_name)
        if expected_value is not None and actual_value != expected_value:
            errors.append(
                f"{field_name}: expected {expected_value}, found {actual_value}"
            )
    return errors


def _write_artifacts(
    config: AuditConfig,
    images: pd.DataFrame,
    subjects: pd.DataFrame,
    duplicates: pd.DataFrame,
    near_duplicates: pd.DataFrame,
    report: dict,
) -> None:
    output_dir = config.metadata_output_dir
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix=".parkindraw-audit-",
        dir=output_dir.parent,
    ) as temporary_directory:
        staging = Path(temporary_directory)
        staged_files = {
            "images_csv": staging / config.artifacts["images_csv"],
            "subjects_csv": staging / config.artifacts["subjects_csv"],
            "duplicate_groups_csv": (
                staging / config.artifacts["duplicate_groups_csv"]
            ),
            "near_duplicate_candidates_csv": (
                staging / config.artifacts["near_duplicate_candidates_csv"]
            ),
            "audit_report_json": (staging / config.artifacts["audit_report_json"]),
        }

        images.to_csv(
            staged_files["images_csv"],
            index=False,
            lineterminator="\n",
        )
        subjects.to_csv(
            staged_files["subjects_csv"],
            index=False,
            lineterminator="\n",
        )
        duplicates.to_csv(
            staged_files["duplicate_groups_csv"],
            index=False,
            lineterminator="\n",
        )
        near_duplicates.to_csv(
            staged_files["near_duplicate_candidates_csv"],
            index=False,
            lineterminator="\n",
        )
        staged_files["audit_report_json"].write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

        for artifact_key, staged_path in staged_files.items():
            destination = output_dir / config.artifacts[artifact_key]
            os.replace(staged_path, destination)


def run_data_audit(
    raw_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    *,
    config: AuditConfig | None = None,
) -> dict:
    """Audit a dataset and atomically publish deterministic metadata artifacts."""
    if config is None:
        if raw_dir is None or output_dir is None:
            raise AuditConfigurationError(
                "Provide config or both raw_dir and output_dir"
            )
        config = AuditConfig.for_paths(raw_dir, output_dir)

    records: list[dict] = []
    unreadable_images: list[dict] = []
    invalid_metadata_files: list[dict] = []

    for filepath in _discover_images(config):
        try:
            record = parse_newhandpd_file(
                filepath,
                config.raw_data_dir,
                dhash_size=config.near_duplicate.hash_size,
            )
        except ImageValidationError as error:
            unreadable_images.append(
                {
                    "filepath": _relative_path(filepath, config.raw_data_dir),
                    "error": str(error),
                }
            )
            continue
        except MetadataParseError as error:
            invalid_metadata_files.append(
                {
                    "filepath": _relative_path(filepath, config.raw_data_dir),
                    "error": str(error),
                }
            )
            continue
        records.append(record.to_dict())

    records.sort(
        key=lambda row: (
            row["class_name"],
            row["drawing_type"],
            row["subject_id"],
            row["drawing_index"],
            row["filename"],
        )
    )

    duplicate_rows, duplicate_group_count = _assign_exact_duplicates(records)
    near_rows, near_candidate_count, near_candidates_truncated = _find_near_duplicates(
        records, config.near_duplicate
    )

    images = pd.DataFrame(records, columns=IMAGE_COLUMNS)
    duplicates = pd.DataFrame(duplicate_rows, columns=DUPLICATE_COLUMNS)
    near_duplicates = pd.DataFrame(
        near_rows,
        columns=NEAR_DUPLICATE_COLUMNS,
    )
    subjects = _build_subjects_dataframe(images)

    total_images = len(images)
    total_subjects = len(subjects)
    healthy_subjects = int((subjects["label"] == 0).sum()) if not subjects.empty else 0
    parkinson_subjects = (
        int((subjects["label"] == 1).sum()) if not subjects.empty else 0
    )

    validation_errors = _expected_count_errors(
        config.expected,
        total_images=total_images,
        total_subjects=total_subjects,
        healthy_subjects=healthy_subjects,
        parkinson_subjects=parkinson_subjects,
    )
    if unreadable_images:
        validation_errors.append(
            f"{len(unreadable_images)} image(s) failed full decoding"
        )
    if invalid_metadata_files:
        validation_errors.append(
            f"{len(invalid_metadata_files)} file(s) failed metadata parsing"
        )

    resolutions: list[dict] = []
    if not images.empty:
        resolution_counts = images.groupby(["width", "height"], sort=True).size()
        resolutions = [
            {"width": int(width), "height": int(height), "count": int(count)}
            for (width, height), count in resolution_counts.items()
        ]

    anomaly_counter: Counter[str] = Counter()
    for anomaly_flags in images.get("anomaly_flags", []):
        if anomaly_flags == "none":
            continue
        anomaly_counter.update(anomaly_flags.split(","))

    report = {
        "audit_schema_version": "1.0",
        "dataset_name": "NewHandPD",
        "dataset_fingerprint_sha256": _dataset_fingerprint(records),
        "status": "passed" if not validation_errors else "failed",
        "validation_errors": validation_errors,
        "total_images": total_images,
        "total_subjects": total_subjects,
        "healthy_subjects": healthy_subjects,
        "parkinson_subjects": parkinson_subjects,
        "drawing_counts": {
            drawing_type: int((images["drawing_type"] == drawing_type).sum())
            if not images.empty
            else 0
            for drawing_type in ("circle", "meander", "spiral")
        },
        "exact_duplicate_groups_count": duplicate_group_count,
        "exact_duplicate_images_count": len(duplicates),
        "near_duplicate_analysis": {
            "enabled": config.near_duplicate.enabled,
            "algorithm": "difference_hash",
            "hash_size": config.near_duplicate.hash_size,
            "max_hamming_distance": (config.near_duplicate.max_hamming_distance),
            "same_drawing_type_only": (config.near_duplicate.same_drawing_type_only),
            "candidate_pairs_count": near_candidate_count,
            "reported_pairs_count": len(near_duplicates),
            "report_truncated": near_candidates_truncated,
            "review_status": "manual_review_required",
        },
        "anomalous_records_count": int((images["anomaly_flags"] != "none").sum())
        if not images.empty
        else 0,
        "anomaly_counts": dict(sorted(anomaly_counter.items())),
        "corrupted_images_count": len(unreadable_images),
        "unreadable_images": unreadable_images,
        "invalid_metadata_files_count": len(invalid_metadata_files),
        "invalid_metadata_files": invalid_metadata_files,
        "resolution_distribution": resolutions,
        "artifacts": config.artifacts,
    }

    _write_artifacts(
        config,
        images,
        subjects,
        duplicates,
        near_duplicates,
        report,
    )
    return report


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit NewHandPD and generate deterministic metadata.",
    )
    parser.add_argument(
        "--config",
        default="configs/data/audit.yaml",
        help="Path to the YAML audit configuration.",
    )
    parser.add_argument(
        "--raw-dir",
        help="Override raw_data_dir from the configuration.",
    )
    parser.add_argument(
        "--output-dir",
        help="Override metadata_output_dir from the configuration.",
    )
    parser.add_argument(
        "--no-near-duplicates",
        action="store_true",
        help="Disable the near-duplicate candidate report.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    config = load_audit_config(
        args.config,
        raw_dir_override=args.raw_dir,
        output_dir_override=args.output_dir,
        near_duplicates_override=False if args.no_near_duplicates else None,
    )
    report = run_data_audit(config=config)

    print(
        "Audit complete: "
        f"{report['total_images']} images, "
        f"{report['total_subjects']} subjects, "
        f"status={report['status']}."
    )
    print(
        "Exact duplicates: "
        f"{report['exact_duplicate_groups_count']} groups / "
        f"{report['exact_duplicate_images_count']} images."
    )
    print(
        "Near-duplicate candidates: "
        f"{report['near_duplicate_analysis']['candidate_pairs_count']} pairs."
    )
    print(f"Artifacts: {config.metadata_output_dir}")
    if report["validation_errors"]:
        for error in report["validation_errors"]:
            print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
