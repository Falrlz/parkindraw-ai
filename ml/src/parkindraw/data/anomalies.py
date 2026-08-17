"""Anomalies, folder schema, and file naming rules for NewHandPD dataset.

This module is the single source of truth for parsing rules and dataset anomalies.
"""

import re
from pathlib import Path

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


def parse_drawing_file(path: Path, folder: str) -> dict:
    """Parse one drawing file and normalize anomalies."""
    if folder not in FOLDER_SCHEMA:
        raise ManifestError(f"Unknown folder in dataset: {folder}")

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
