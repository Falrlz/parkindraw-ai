"""Dataset loading for the NewHandPD static-image subset.

The class and drawing type come from the folder name; the subject ID and
drawing index are parsed from the file name. Source files are never modified.

This module is the single source of truth for parsing rules. It knows nothing
about train/test splits, and it reads no pixels while building the manifest.
"""

import re
from pathlib import Path

import pandas as pd

# The folder determines both class and drawing type. A file name never
# determines the class: every circle uses the "P" prefix as a participant index
# in both folders (HealthyCircle/circA-P1.jpg and PatientCircle/circA-P1.jpg),
# so trusting the name would mislabel every healthy circle.
FOLDER_SCHEMA = {
    "HealthyCircle": ("Healthy", 0, "circle"),
    "HealthyMeander": ("Healthy", 0, "meander"),
    "HealthySpiral": ("Healthy", 0, "spiral"),
    "PatientCircle": ("Parkinson", 1, "circle"),
    "PatientMeander": ("Parkinson", 1, "meander"),
    "PatientSpiral": ("Parkinson", 1, "spiral"),
}

FILENAME_PATTERNS = {
    "circle": re.compile(r"circA-[HhPp](\d+)$", re.IGNORECASE),
    "meander": re.compile(r"mea(\d+)-[HhPp](\d+)$", re.IGNORECASE),
    "spiral": re.compile(r"sp(\d+)-[HhPp](\d+)$", re.IGNORECASE),
}

# The dataset protocol defines four meanders per subject, but the source
# archive ships mea1, mea2, mea3, and mea5 for subject P08. The anomaly is
# mapped explicitly rather than swallowed, so an unexpected index still fails.
DRAWING_INDEX_OVERRIDES = {("PatientMeander", "mea5-p8"): 4}

# The dataset provides one circle and four of each other drawing per subject.
CIRCLE_DRAWING_INDEX = 1
MAX_DRAWING_INDEX = 4

MANIFEST_COLUMNS = [
    "filepath",
    "filename",
    "class_name",
    "label",
    "drawing_type",
    "drawing_index",
    "subject_id",
]


class ManifestError(ValueError):
    """Raised when a folder or filename does not follow the expected schema."""


def _parse_file(path: Path, folder: str) -> dict:
    class_name, label, drawing_type = FOLDER_SCHEMA[folder]
    stem = path.stem

    match = FILENAME_PATTERNS[drawing_type].fullmatch(stem)
    if match is None:
        raise ManifestError(
            f"Filename does not match the {drawing_type} schema: {path.name}"
        )

    if drawing_type == "circle":
        drawing_index, subject_number = CIRCLE_DRAWING_INDEX, match.group(1)
    else:
        drawing_index, subject_number = int(match.group(1)), match.group(2)

    override = DRAWING_INDEX_OVERRIDES.get((folder, stem.lower()))
    if override is not None:
        drawing_index = override
    elif drawing_index not in range(1, MAX_DRAWING_INDEX + 1):
        raise ManifestError(
            f"Drawing index {drawing_index} outside 1..{MAX_DRAWING_INDEX}: {path.name}"
        )

    # The subject ID follows the class from the folder, not the filename prefix.
    prefix = "H" if label == 0 else "P"
    return {
        "filepath": f"{folder}/{path.name}",
        "filename": path.name,
        "class_name": class_name,
        "label": label,
        "drawing_type": drawing_type,
        "drawing_index": drawing_index,
        "subject_id": f"{prefix}{int(subject_number):02d}",
    }


def build_manifest(
    raw_dir: str | Path = "data/raw",
    *,
    extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png"),
) -> pd.DataFrame:
    """Scan `raw_dir` and return one row per image.

    Row order is deterministic so that splitting with the same seed always
    yields an identical partition.
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
                rows.append(_parse_file(path, folder))

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


class DrawingDataset:
    """PyTorch Dataset that reads images according to a manifest.

    Torch and PIL are imported lazily so this module stays usable for building
    manifests on machines without the training dependencies installed.
    """

    def __init__(
        self,
        manifest: pd.DataFrame,
        raw_dir: str | Path = "data/raw",
        transform=None,
    ) -> None:
        self.manifest = manifest.reset_index(drop=True)
        self.raw_dir = Path(raw_dir)
        self.transform = transform

    def __len__(self) -> int:
        return len(self.manifest)

    def __getitem__(self, index: int):
        from PIL import Image

        row = self.manifest.iloc[index]
        with Image.open(self.raw_dir / row["filepath"]) as image:
            sample = image.convert("RGB")
        if self.transform is not None:
            sample = self.transform(sample)
        return sample, int(row["label"])
