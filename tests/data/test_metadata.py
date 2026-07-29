"""Unit tests for strict NewHandPD metadata parsing."""

from pathlib import Path

import pytest
from PIL import Image

from parkindraw.data.metadata import (
    ImageValidationError,
    MetadataParseError,
    normalize_subject_id,
    parse_newhandpd_file,
)


def create_image(root: Path, folder: str, filename: str) -> Path:
    path = root / folder / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (32, 24), color="white").save(path)
    return path


@pytest.mark.parametrize(
    ("raw_id", "expected"),
    [
        ("H1", "H01"),
        ("h1", "H01"),
        ("P2", "P02"),
        ("p27", "P27"),
        ("H38", "H38"),
    ],
)
def test_normalize_subject_id(raw_id: str, expected: str) -> None:
    assert normalize_subject_id(raw_id) == expected


def test_parse_normal_meander_from_synthetic_image(tmp_path: Path) -> None:
    filepath = create_image(tmp_path, "HealthyMeander", "mea1-H1.jpg")

    record = parse_newhandpd_file(filepath, tmp_path)

    assert record.class_name == "Healthy"
    assert record.label == 0
    assert record.drawing_type == "meander"
    assert record.drawing_index == 1
    assert record.raw_subject_token == "H1"
    assert record.subject_id == "H01"
    assert record.channels == 3
    assert record.anomaly_flags == "none"


def test_mea5_p8_known_anomaly_maps_to_logical_index_four(
    tmp_path: Path,
) -> None:
    filepath = create_image(tmp_path, "PatientMeander", "mea5-P8.jpg")

    record = parse_newhandpd_file(filepath, tmp_path)

    assert record.drawing_index == 4
    assert record.raw_filename == "mea5-P8.jpg"
    assert record.raw_subject_token == "P8"
    assert record.subject_id == "P08"
    assert "non_standard_index_mea5_mapped_to_4" in record.anomaly_flags


def test_healthy_circle_preserves_mismatched_source_token(
    tmp_path: Path,
) -> None:
    filepath = create_image(tmp_path, "HealthyCircle", "circA-P1.jpg")

    record = parse_newhandpd_file(filepath, tmp_path)

    assert record.class_name == "Healthy"
    assert record.raw_subject_token == "P1"
    assert record.raw_subject_id == "H1"
    assert record.subject_id == "H01"
    assert "folder_class_mismatch_p_token_in_healthy_folder" in record.anomaly_flags


def test_lowercase_source_token_is_flagged(tmp_path: Path) -> None:
    filepath = create_image(tmp_path, "PatientCircle", "circA-p27.jpg")

    record = parse_newhandpd_file(filepath, tmp_path)

    assert record.raw_subject_token == "p27"
    assert record.subject_id == "P27"
    assert "lowercase_subject_token" in record.anomaly_flags


@pytest.mark.parametrize(
    ("folder", "filename"),
    [
        ("PatientMeander", "mea9-P2.jpg"),
        ("PatientSpiral", "sp0-P2.jpg"),
        ("PatientMeander", "unexpected-P2.jpg"),
        ("HealthyCircle", "circle-H1.jpg"),
    ],
)
def test_invalid_filename_or_index_is_rejected(
    tmp_path: Path,
    folder: str,
    filename: str,
) -> None:
    filepath = create_image(tmp_path, folder, filename)

    with pytest.raises(MetadataParseError):
        parse_newhandpd_file(filepath, tmp_path)


def test_unknown_folder_is_rejected(tmp_path: Path) -> None:
    filepath = create_image(tmp_path, "OtherCircle", "circA-H1.jpg")

    with pytest.raises(MetadataParseError, match="Unknown NewHandPD folder"):
        parse_newhandpd_file(filepath, tmp_path)


def test_truncated_image_that_has_readable_header_is_rejected(
    tmp_path: Path,
) -> None:
    filepath = create_image(tmp_path, "HealthyCircle", "circA-H1.png")
    filepath.write_bytes(filepath.read_bytes()[:100])

    with pytest.raises(ImageValidationError, match="Image validation failed"):
        parse_newhandpd_file(filepath, tmp_path)
