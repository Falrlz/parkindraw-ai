"""Test aturan parsing manifest."""

import pytest

from parkindraw.data.dataset import (
    DrawingDataset,
    ManifestError,
    build_manifest,
    filter_drawing,
)


def test_setiap_gambar_punya_record(raw_dir, total_images):
    assert len(build_manifest(raw_dir)) == total_images


def test_class_diambil_dari_folder_bukan_nama_file(raw_dir):
    """`HealthyCircle/circA-P1.jpg` harus jadi H01, bukan P01."""
    manifest = build_manifest(raw_dir)
    circle = manifest[
        (manifest.drawing_type == "circle") & (manifest.class_name == "Healthy")
    ]

    assert circle.filename.str.contains("-P", case=False).all()
    assert circle.subject_id.str.startswith("H").all()
    assert (circle.label == 0).all()


def test_subject_id_dinormalkan_dengan_nol_di_depan(raw_dir):
    manifest = build_manifest(raw_dir)
    assert "H01" in set(manifest.subject_id)
    assert "P01" in set(manifest.subject_id)


def test_token_huruf_kecil_tetap_terbaca(raw_dir, lowercase_subject):
    manifest = build_manifest(raw_dir)
    baris = manifest[manifest.filename == f"circA-p{lowercase_subject}.jpg"]
    assert len(baris) == 1
    assert baris.iloc[0].subject_id == f"H{lowercase_subject:02d}"


def test_mea5_dipetakan_ke_index_4(raw_dir, mea5_subject):
    manifest = build_manifest(raw_dir)
    subjek = f"P{mea5_subject:02d}"
    meander = manifest[
        (manifest.subject_id == subjek) & (manifest.drawing_type == "meander")
    ]
    assert sorted(meander.drawing_index) == [1, 2, 3, 4]
    assert f"mea5-P{mea5_subject}.jpg" in set(meander.filename)


def test_setiap_subjek_punya_satu_circle_empat_meander_empat_spiral(raw_dir):
    manifest = build_manifest(raw_dir)
    tabel = manifest.pivot_table(
        index="subject_id",
        columns="drawing_type",
        values="filepath",
        aggfunc="count",
    )
    assert (tabel["circle"] == 1).all()
    assert (tabel["meander"] == 4).all()
    assert (tabel["spiral"] == 4).all()


def test_himpunan_subjek_identik_di_ketiga_drawing(raw_dir):
    """Syarat wajib agar split yang sama dapat dipakai ketiga model."""
    manifest = build_manifest(raw_dir)
    himpunan = {d: set(g.subject_id) for d, g in manifest.groupby("drawing_type")}
    assert himpunan["circle"] == himpunan["meander"] == himpunan["spiral"]


def test_satu_subject_id_hanya_satu_class(raw_dir):
    manifest = build_manifest(raw_dir)
    assert manifest.groupby("subject_id").class_name.nunique().max() == 1


def test_tidak_ada_kombinasi_ganda(raw_dir):
    manifest = build_manifest(raw_dir)
    kunci = ["subject_id", "drawing_type", "drawing_index"]
    assert not manifest.duplicated(kunci).any()


def test_hasil_deterministik(raw_dir):
    assert build_manifest(raw_dir).equals(build_manifest(raw_dir))


def test_filter_drawing(raw_dir, total_subjects):
    manifest = build_manifest(raw_dir)
    assert len(filter_drawing(manifest, "circle")) == total_subjects
    assert len(filter_drawing(manifest, "meander")) == total_subjects * 4
    assert len(filter_drawing(manifest, "spiral")) == total_subjects * 4


def test_filter_drawing_menolak_tipe_tak_dikenal(raw_dir):
    manifest = build_manifest(raw_dir)
    with pytest.raises(ValueError, match="tidak dikenal"):
        filter_drawing(manifest, "wave")


def test_nama_file_tidak_sesuai_skema_ditolak(raw_dir):
    (raw_dir / "HealthySpiral" / "gambar-aneh.jpg").write_bytes(b"x")
    with pytest.raises(ManifestError, match="tidak sesuai skema"):
        build_manifest(raw_dir)


def test_drawing_index_di_luar_rentang_ditolak(raw_dir):
    from PIL import Image

    Image.new("RGB", (8, 8)).save(raw_dir / "HealthySpiral" / "sp9-H1.jpg")
    with pytest.raises(ManifestError, match="di luar 1..4"):
        build_manifest(raw_dir)


def test_folder_hilang_ditolak(raw_dir):
    for path in (raw_dir / "PatientSpiral").iterdir():
        path.unlink()
    (raw_dir / "PatientSpiral").rmdir()
    with pytest.raises(FileNotFoundError, match="Folder wajib"):
        build_manifest(raw_dir)


def test_raw_dir_tidak_ada_ditolak(tmp_path):
    with pytest.raises(FileNotFoundError, match="tidak ditemukan"):
        build_manifest(tmp_path / "tidak-ada")


def test_drawing_dataset_membaca_gambar(raw_dir):
    manifest = filter_drawing(build_manifest(raw_dir), "spiral")
    dataset = DrawingDataset(manifest, raw_dir)

    gambar, label = dataset[0]
    assert len(dataset) == len(manifest)
    assert gambar.mode == "RGB"
    assert label in (0, 1)


def test_drawing_dataset_menerapkan_transform(raw_dir):
    manifest = filter_drawing(build_manifest(raw_dir), "circle")
    dataset = DrawingDataset(manifest, raw_dir, transform=lambda image: "diproses")
    assert dataset[0][0] == "diproses"
