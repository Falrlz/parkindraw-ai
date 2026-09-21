"""Tests for manifest loading, saving, and filtering helpers."""

from pathlib import Path

import pandas as pd
import pytest

from src.data.manifest import filter_holdout, load_manifest, save_manifest


def test_save_and_load_manifest(tmp_path: Path):
    df = pd.DataFrame(
        {
            "filepath": ["HealthyCircle/circA-P1.jpg"],
            "drawing_type": ["circle"],
            "partition": ["holdout"],
        }
    )
    dest = tmp_path / "splits" / "master_manifest.csv"
    saved = save_manifest(df, dest)
    assert saved.is_file()

    loaded = load_manifest(dest)
    assert len(loaded) == 1
    assert loaded.iloc[0]["filepath"] == "HealthyCircle/circA-P1.jpg"

    loaded_dir = load_manifest(tmp_path / "splits")
    assert len(loaded_dir) == 1


def test_load_manifest_non_existent():
    with pytest.raises(FileNotFoundError):
        load_manifest("non_existent_dir")


def test_filter_holdout():
    df = pd.DataFrame(
        {
            "subject_id": ["H01", "H02", "P01"],
            "partition": ["development", "holdout", "development"],
        }
    )
    holdout = filter_holdout(df)
    assert len(holdout) == 1
    assert holdout.iloc[0]["subject_id"] == "H02"


def test_filter_holdout_missing_column():
    df = pd.DataFrame({"subject_id": ["H01"]})
    with pytest.raises(ValueError, match="does not contain a 'partition' column"):
        filter_holdout(df)
