"""Quality gate: split tidak boleh membocorkan subjek antar-partisi."""

import json

import pandas as pd
import pytest

from parkindraw.data.dataset import build_manifest
from parkindraw.data.splits import (
    SplitError,
    build_folds,
    build_holdout,
    build_sessions,
    run_split,
    verify_no_leakage,
)

N_SPLITS = 3


@pytest.fixture
def hasil_split(raw_dir, tmp_path):
    """Jalankan pipeline split lengkap dan kembalikan artifact-nya."""
    output = tmp_path / "splits"
    ringkasan = run_split(raw_dir, output, n_splits=N_SPLITS)
    return {
        "dir": output,
        "ringkasan": ringkasan,
        "holdout": pd.read_csv(output / "holdout.csv"),
        "folds": [pd.read_csv(output / f"fold_{i}.csv") for i in range(N_SPLITS)],
        "sessions": pd.read_csv(output / "sessions.csv"),
    }


def _subjek(frame, kolom, nilai):
    return set(frame.loc[frame[kolom] == nilai, "subject_id"])


# --- Quality gate utama ---------------------------------------------------


def test_holdout_dan_development_tidak_beririsan(hasil_split):
    holdout = hasil_split["holdout"]
    assert not (
        _subjek(holdout, "partition", "holdout")
        & _subjek(holdout, "partition", "development")
    )


def test_train_dan_validation_tidak_beririsan(hasil_split):
    for nomor, fold in enumerate(hasil_split["folds"]):
        bocor = _subjek(fold, "split", "train") & _subjek(fold, "split", "validation")
        assert not bocor, f"fold_{nomor} membocorkan subjek: {sorted(bocor)}"


def test_fold_tidak_pernah_menyentuh_holdout(hasil_split):
    terkunci = _subjek(hasil_split["holdout"], "partition", "holdout")
    for nomor, fold in enumerate(hasil_split["folds"]):
        bocor = terkunci & set(fold.subject_id)
        assert not bocor, f"fold_{nomor} memakai subjek holdout: {sorted(bocor)}"


def test_tidak_ada_gambar_yang_muncul_di_dua_partisi(raw_dir, hasil_split):
    """Jaminan level gambar, bukan hanya level subjek."""
    manifest = build_manifest(raw_dir)
    holdout = hasil_split["holdout"]
    terkunci = _subjek(holdout, "partition", "holdout")
    dev = _subjek(holdout, "partition", "development")

    gambar_terkunci = set(manifest.loc[manifest.subject_id.isin(terkunci), "filepath"])
    gambar_dev = set(manifest.loc[manifest.subject_id.isin(dev), "filepath"])
    assert not (gambar_terkunci & gambar_dev)


# --- Kelengkapan dan konsistensi -----------------------------------------


def test_semua_subjek_mendapat_partisi(raw_dir, hasil_split, total_subjects):
    holdout = hasil_split["holdout"]
    assert len(holdout) == total_subjects
    assert set(holdout.subject_id) == set(build_manifest(raw_dir).subject_id)
    assert set(holdout.partition) == {"development", "holdout"}


def test_setiap_subjek_development_divalidasi_tepat_sekali(hasil_split):
    dev = _subjek(hasil_split["holdout"], "partition", "development")
    hitung = (
        pd.concat(hasil_split["folds"])
        .query("split == 'validation'")
        .subject_id.value_counts()
    )
    assert set(hitung.index) == dev
    assert (hitung == 1).all()


def test_kedua_class_terwakili_di_setiap_partisi(hasil_split):
    holdout = hasil_split["holdout"]
    for partisi in ("development", "holdout"):
        kelas = set(holdout.loc[holdout.partition == partisi, "class_name"])
        assert kelas == {"Healthy", "Parkinson"}


# --- Application-matched session ------------------------------------------


def test_session_hanya_untuk_subjek_holdout(hasil_split):
    terkunci = _subjek(hasil_split["holdout"], "partition", "holdout")
    sessions = hasil_split["sessions"]
    assert set(sessions.subject_id) == terkunci
    assert len(sessions) == len(terkunci) * 4


def test_setiap_session_memakai_satu_gambar_tiap_drawing(hasil_split):
    sessions = hasil_split["sessions"]
    assert sessions[["circle", "meander", "spiral"]].notna().all().all()
    assert sessions.session_id.is_unique


def test_circle_digunakan_ulang_di_empat_session(hasil_split):
    """Dataset hanya menyediakan satu Circle per subjek."""
    for _, group in hasil_split["sessions"].groupby("subject_id"):
        assert group.circle.nunique() == 1
        assert group.meander.nunique() == 4
        assert group.spiral.nunique() == 4


def test_session_memakai_subjek_yang_sama_untuk_ketiga_drawing(raw_dir, hasil_split):
    manifest = build_manifest(raw_dir).set_index("filepath")
    for baris in hasil_split["sessions"].itertuples():
        subjek = {
            manifest.loc[getattr(baris, d), "subject_id"]
            for d in ("circle", "meander", "spiral")
        }
        assert subjek == {baris.subject_id}


# --- Reproducibility ------------------------------------------------------


def test_seed_sama_menghasilkan_split_identik(raw_dir, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    run_split(raw_dir, a, seed=7)
    run_split(raw_dir, b, seed=7)
    for nama in ("holdout.csv", "fold_0.csv", "sessions.csv"):
        assert (a / nama).read_text() == (b / nama).read_text()


def test_seed_berbeda_menghasilkan_split_berbeda(raw_dir, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    run_split(raw_dir, a, seed=1)
    run_split(raw_dir, b, seed=99)
    assert (a / "holdout.csv").read_text() != (b / "holdout.csv").read_text()


def test_config_mencatat_seed_dan_ukuran(hasil_split):
    config = json.loads((hasil_split["dir"] / "split_config.json").read_text())
    assert config["seed"] == 42
    assert config["n_splits"] == N_SPLITS
    assert (
        config["holdout_subjects"] + config["development_subjects"]
        == (config["total_subjects"])
    )


def test_seluruh_artifact_ditulis(hasil_split):
    diharapkan = {
        "holdout.csv",
        "sessions.csv",
        "split_config.json",
        *(f"fold_{i}.csv" for i in range(N_SPLITS)),
    }
    assert {p.name for p in hasil_split["dir"].iterdir()} == diharapkan


# --- Penjaga internal -----------------------------------------------------


def test_verify_no_leakage_mendeteksi_pelanggaran(raw_dir):
    """Penjaga harus benar-benar gagal ketika holdout bocor ke fold."""
    manifest = build_manifest(raw_dir)
    holdout = build_holdout(manifest)
    dev = holdout.loc[holdout.partition == "development", "subject_id"]
    folds = build_folds(manifest, dev, n_splits=N_SPLITS)

    terkunci = holdout.loc[holdout.partition == "holdout", "subject_id"].iloc[0]
    tercemar = folds[0].copy()
    tercemar.loc[len(tercemar)] = {
        "subject_id": terkunci,
        "class_name": "Healthy",
        "label": 0,
        "split": "train",
    }

    with pytest.raises(SplitError, match="holdout muncul"):
        verify_no_leakage(holdout, [tercemar])


def test_build_sessions_menolak_subjek_tanpa_circle(raw_dir):
    manifest = build_manifest(raw_dir)
    subjek = manifest.subject_id.iloc[0]
    tanpa_circle = manifest.drop(
        manifest[
            (manifest.subject_id == subjek) & (manifest.drawing_type == "circle")
        ].index
    )
    with pytest.raises(SplitError, match="tepat satu circle"):
        build_sessions(tanpa_circle, pd.Series([subjek]))
