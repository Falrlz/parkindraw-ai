"""Tests for manifest parsing rules without dataset dependency."""

import pytest

from src.data.anomalies import ManifestError
from src.data.manifest import build_manifest, filter_drawing

MEANDERS_PER_SUBJECT = 4
SPIRALS_PER_SUBJECT = 4


def test_every_image_gets_a_record(raw_dir, total_images):
    assert len(build_manifest(raw_dir)) == total_images


def test_class_comes_from_the_folder_not_the_filename(raw_dir):
    """`HealthyCircle/circA-P1.jpg` must become H01, never P01."""
    manifest = build_manifest(raw_dir)
    circles = manifest[
        (manifest.drawing_type == "circle") & (manifest.class_name == "Healthy")
    ]

    assert circles.filename.str.contains("-P", case=False).all()
    assert circles.subject_id.str.startswith("H").all()
    assert (circles.label == 0).all()


def test_subject_id_is_zero_padded(raw_dir):
    manifest = build_manifest(raw_dir)
    assert "H01" in set(manifest.subject_id)
    assert "P01" in set(manifest.subject_id)


def test_lowercase_token_is_still_parsed(raw_dir, lowercase_subject):
    manifest = build_manifest(raw_dir)
    row = manifest[manifest.filename == f"circA-p{lowercase_subject}.jpg"]
    assert len(row) == 1
    assert row.iloc[0].subject_id == f"H{lowercase_subject:02d}"


def test_mea5_is_mapped_to_index_4(raw_dir, mea5_subject):
    manifest = build_manifest(raw_dir)
    subject = f"P{mea5_subject:02d}"
    meanders = manifest[
        (manifest.subject_id == subject) & (manifest.drawing_type == "meander")
    ]
    assert sorted(meanders.drawing_index) == [1, 2, 3, 4]
    assert f"mea5-P{mea5_subject}.jpg" in set(meanders.filename)


def test_each_subject_has_one_circle_four_meanders_four_spirals(raw_dir):
    manifest = build_manifest(raw_dir)
    counts = manifest.pivot_table(
        index="subject_id",
        columns="drawing_type",
        values="filepath",
        aggfunc="count",
    )
    assert (counts["circle"] == 1).all()
    assert (counts["meander"] == MEANDERS_PER_SUBJECT).all()
    assert (counts["spiral"] == SPIRALS_PER_SUBJECT).all()


def test_subject_sets_are_identical_across_drawing_types(raw_dir):
    """Precondition for reusing one split across all three models."""
    manifest = build_manifest(raw_dir)
    subjects = {d: set(g.subject_id) for d, g in manifest.groupby("drawing_type")}
    assert subjects["circle"] == subjects["meander"] == subjects["spiral"]


def test_a_subject_id_maps_to_exactly_one_class(raw_dir):
    manifest = build_manifest(raw_dir)
    assert manifest.groupby("subject_id").class_name.nunique().max() == 1


def test_no_duplicate_drawing_entries(raw_dir):
    manifest = build_manifest(raw_dir)
    key = ["subject_id", "drawing_type", "drawing_index"]
    assert not manifest.duplicated(key).any()


def test_manifest_is_deterministic(raw_dir):
    assert build_manifest(raw_dir).equals(build_manifest(raw_dir))


def test_filter_drawing(raw_dir, total_subjects):
    manifest = build_manifest(raw_dir)
    assert len(filter_drawing(manifest, "circle")) == total_subjects
    assert (
        len(filter_drawing(manifest, "meander"))
        == total_subjects * MEANDERS_PER_SUBJECT
    )
    assert (
        len(filter_drawing(manifest, "spiral")) == total_subjects * SPIRALS_PER_SUBJECT
    )


def test_filter_drawing_rejects_an_unknown_type(raw_dir):
    manifest = build_manifest(raw_dir)
    with pytest.raises(ValueError, match="Unknown drawing type"):
        filter_drawing(manifest, "wave")


def test_filename_off_schema_is_rejected(raw_dir):
    (raw_dir / "HealthySpiral" / "odd-image.jpg").write_bytes(b"x")
    with pytest.raises(ManifestError, match="does not match"):
        build_manifest(raw_dir)


def test_drawing_index_out_of_range_is_rejected(raw_dir):
    from PIL import Image

    Image.new("RGB", (8, 8)).save(raw_dir / "HealthySpiral" / "sp9-H1.jpg")
    with pytest.raises(ManifestError, match="outside 1..4"):
        build_manifest(raw_dir)


def test_missing_folder_is_rejected(raw_dir):
    for path in (raw_dir / "PatientSpiral").iterdir():
        path.unlink()
    (raw_dir / "PatientSpiral").rmdir()
    with pytest.raises(FileNotFoundError, match="Required folder"):
        build_manifest(raw_dir)


def test_missing_raw_dir_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError, match="Dataset folder not found"):
        build_manifest(tmp_path / "does-not-exist")
