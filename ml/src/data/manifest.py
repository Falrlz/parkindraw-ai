"""Dataset scanning and audited manifest construction."""

from pathlib import Path

import pandas as pd

from src.config.config import (
    BASE_MANIFEST_COLUMNS,
    FOLDER_SCHEMA,
    MANIFEST_COLUMNS,
    MASTER_MANIFEST_PATH,
    RAW_DATA_DIR,
    SPLITS_DIR,
)
from src.data.anomalies import parse_drawing_file
from src.data.hashing import build_clusters, cluster_ids, hash_images
from src.utils.logger import get_logger

logger = get_logger(__name__)


def build_manifest(
    raw_dir: str | Path = RAW_DATA_DIR,
    ) -> pd.DataFrame:

    """Scan raw images, validate anomalies, hash bytes, and return complete manifest."""
    root = Path(raw_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"Dataset folder not found: {root}")

    # 1. Pindai folder & parse nama file (anomalies.py)
    rows = []
    for folder in sorted(FOLDER_SCHEMA):
        folder_path = root / folder
        if not folder_path.is_dir():
            raise FileNotFoundError(f"Required folder not found: {folder_path}")

        for path in sorted(folder_path.iterdir(), key=lambda p: p.name.casefold()):
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                rows.append(parse_drawing_file(path, folder))

    manifest = pd.DataFrame(rows, columns=BASE_MANIFEST_COLUMNS).sort_values(
        ["drawing_type", "subject_id", "drawing_index"], ignore_index=True
    )

    # 2. Audit duplikasi byte & cluster pasien kembar (hashing.py)
    hashes = hash_images(manifest, root)
    clusters = build_clusters(manifest, hashes)

    manifest["image_hash"] = hashes.values
    manifest["cluster_id"] = cluster_ids(manifest["subject_id"], clusters).values

    logger.info(
        "Manifest complete: %d drawings, %d subjects (%d clusters).",
        len(manifest),
        manifest["subject_id"].nunique(),
        manifest["cluster_id"].nunique(),
    )
    return manifest[MANIFEST_COLUMNS]


def filter_drawing(
    manifest: pd.DataFrame, 
    drawing_type: str
    ) -> pd.DataFrame:

    """Filter manifest rows for a single drawing type (circle, meander, or spiral)."""
    if drawing_type not in {"circle", "meander", "spiral"}:
        raise ValueError(f"Unknown drawing type: {drawing_type}")
    return manifest.loc[manifest["drawing_type"] == drawing_type].reset_index(drop=True)


def load_manifest(
    splits_dir: str | Path = SPLITS_DIR
    ) -> pd.DataFrame:

    """Load master_manifest.csv from the splits directory."""
    path = Path(splits_dir)
    manifest_path = path if path.is_file() else path / "master_manifest.csv"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Master manifest not found at: {manifest_path}")
    return pd.read_csv(manifest_path)


def save_manifest(
    df: pd.DataFrame, 
    output_path: str | Path = MASTER_MANIFEST_PATH
    ) -> Path:

    """Export master manifest DataFrame to CSV on disk."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("Saved %d manifest records to %s", len(df), path)
    return path


def filter_holdout(
    manifest: pd.DataFrame
    ) -> pd.DataFrame:

    """Extract rows belonging to the locked holdout test partition."""
    if "partition" not in manifest.columns:
        raise ValueError("Manifest does not contain a 'partition' column.")
    return manifest.loc[manifest["partition"] == "holdout"].reset_index(drop=True)
