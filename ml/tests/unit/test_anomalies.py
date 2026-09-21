"""Unit tests for filename parsing, anomaly overrides, and subject formatting."""

from pathlib import Path

import pytest

from src.data.anomalies import (
    ManifestError,
    correct_drawing_index,
    extract_drawing_tokens,
    format_subject_id,
    parse_drawing_file,
)


def test_extract_drawing_tokens_circle():
    index, subject_num = extract_drawing_tokens("circle", "circA-P01", "circA-P01.jpg")
    assert index == 1
    assert subject_num == 1


def test_extract_drawing_tokens_meander():
    index, subject_num = extract_drawing_tokens("meander", "mea3-H05", "mea3-H05.jpg")
    assert index == 3
    assert subject_num == 5


def test_extract_drawing_tokens_spiral():
    index, subject_num = extract_drawing_tokens("spiral", "sp2-p08", "sp2-p08.jpg")
    assert index == 2
    assert subject_num == 8


def test_extract_drawing_tokens_invalid_filename_raises():
    with pytest.raises(ManifestError, match="does not match"):
        extract_drawing_tokens("spiral", "invalid_name", "invalid_name.jpg")


def test_extract_drawing_tokens_unsupported_type_raises():
    with pytest.raises(ManifestError, match="Unsupported drawing type"):
        extract_drawing_tokens("cube", "cube1-P01", "cube1-P01.jpg")


def test_correct_drawing_index_normal_range():
    assert correct_drawing_index("PatientMeander", "mea2-p01", 2, "mea2-p01.jpg") == 2


def test_correct_drawing_index_p08_anomaly_override():
    assert correct_drawing_index("PatientMeander", "mea5-p8", 5, "mea5-p8.jpg") == 4


def test_correct_drawing_index_out_of_bounds_raises():
    with pytest.raises(ManifestError, match="outside 1..4"):
        correct_drawing_index("PatientMeander", "mea6-p01", 6, "mea6-p01.jpg")


def test_format_subject_id_healthy():
    assert format_subject_id(0, 1) == "H01"
    assert format_subject_id(0, 15) == "H15"


def test_format_subject_id_parkinson():
    assert format_subject_id(1, 8) == "P08"
    assert format_subject_id(1, 25) == "P25"


def test_parse_drawing_file_success():
    result = parse_drawing_file(Path("data/raw/PatientSpiral/sp1-p08.jpg"), "PatientSpiral")
    assert result == {
        "filepath": "PatientSpiral/sp1-p08.jpg",
        "filename": "sp1-p08.jpg",
        "class_name": "Parkinson",
        "label": 1,
        "drawing_type": "spiral",
        "drawing_index": 1,
        "subject_id": "P08",
    }


def test_parse_drawing_file_unknown_folder_raises():
    with pytest.raises(ManifestError, match="Unknown folder"):
        parse_drawing_file(Path("invalid/sp1-p01.jpg"), "UnknownFolder")
