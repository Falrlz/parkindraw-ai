"""Dataset scanning and manifest building for the NewHandPD static-image subset.

This module scans raw image files into a structured DataFrame.
It reads no pixels and has no knowledge of training/test splits.
"""

from pathlib import Path

import pandas as pd

from parkindraw.data.anomalies import (
    FOLDER_SCHEMA,
    MANIFEST_COLUMNS,
    parse_drawing_file,
)


def build_manifest(
    raw_dir: str | Path = "data/raw",
    *,
    extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png"),
) -> pd.DataFrame:
    """Scan `raw_dir` and return one row per image.

    Row order is deterministic so that downstream processing yields identical
    partitions.
    """
    root = Path(raw_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"Dataset folder not found: {root}")

    rows = []
    for folder in sorted(FOLDER_SCHEMA):
        folder_path = root / folder
        if not folder_path.is_dir():
            raise FileNotFoundError(f"Required folder not found: {folder_path}")
        for path in sorted(folder_path.iterdir(), key=lambda p: p.name.casefold()):
            if path.is_file() and path.suffix.lower() in extensions:
                rows.append(parse_drawing_file(path, folder))

    manifest = pd.DataFrame(rows, columns=MANIFEST_COLUMNS)
    return manifest.sort_values(
        ["drawing_type", "subject_id", "drawing_index"],
        ignore_index=True,
    )


def filter_drawing(manifest: pd.DataFrame, drawing_type: str) -> pd.DataFrame:
    """Select the subset for a single drawing type, to train one model."""
    if drawing_type not in {"circle", "meander", "spiral"}:
        raise ValueError(f"Unknown drawing type: {drawing_type}")
    return manifest.loc[manifest["drawing_type"] == drawing_type].reset_index(drop=True)
