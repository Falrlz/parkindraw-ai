"""Folder schema, file naming rules, and anomaly overrides for NewHandPD."""

from pathlib import Path

from src.config.config import (
    CIRCLE_DRAWING_INDEX,
    DRAWING_INDEX_OVERRIDES,
    FILENAME_PATTERNS,
    FOLDER_SCHEMA,
    MAX_DRAWING_INDEX,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ManifestError(ValueError):
    """Raised when a folder or filename does not follow the expected schema."""


def extract_drawing_tokens(
    drawing_type: str, 
    stem: str, 
    filename: str
    ) -> tuple[int, int]:

    """Extract raw drawing index and subject number from filename stem using regex."""
    pattern = FILENAME_PATTERNS.get(drawing_type)
    if pattern is None:
        raise ManifestError(f"Unsupported drawing type: {drawing_type}")

    match = pattern.fullmatch(stem)
    if match is None:
        raise ManifestError(
            f"Filename does not match the {drawing_type} schema: {filename}"
        )

    if drawing_type == "circle":
        return CIRCLE_DRAWING_INDEX, int(match.group(1))
    return int(match.group(1)), int(match.group(2))


def correct_drawing_index(
    folder: str, 
    stem: str, 
    raw_index: int, 
    filename: str
    ) -> int:

    """Apply known anomaly overrides and validate allowed drawing index range (1..4)."""

    override = DRAWING_INDEX_OVERRIDES.get((folder, stem.lower()))
    if override is not None:
        return override
    if raw_index not in range(1, MAX_DRAWING_INDEX + 1):
        raise ManifestError(
            f"Drawing index {raw_index} outside 1..{MAX_DRAWING_INDEX}: {filename}"
        )
    return raw_index


def format_subject_id(
    label: int, 
    subject_number: int
    ) -> str:

    """Format subject number into a standard 2-digit identifier (e.g. 'H01', 'P08')."""
    prefix = "H" if label == 0 else "P"
    return f"{prefix}{subject_number:02d}"


def parse_drawing_file(
    path: Path, 
    folder: str
    ) -> dict:
    
    """Parse one drawing file, validate against schema, and normalize anomalies."""
    if folder not in FOLDER_SCHEMA:
        raise ManifestError(f"Unknown folder in dataset: {folder}")

    class_name, label, drawing_type = FOLDER_SCHEMA[folder]
    stem = path.stem

    raw_index, subject_number = extract_drawing_tokens(drawing_type, stem, path.name)
    drawing_index = correct_drawing_index(folder, stem, raw_index, path.name)
    subject_id = format_subject_id(label, subject_number)

    return {
        "filepath": f"{folder}/{path.name}",
        "filename": path.name,
        "class_name": class_name,
        "label": label,
        "drawing_type": drawing_type,
        "drawing_index": drawing_index,
        "subject_id": subject_id,
    }
