"""Metadata models and strict parsing utilities for NewHandPD images."""

import hashlib
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError


class MetadataParseError(ValueError):
    """Raised when a path does not follow the supported NewHandPD schema."""


class ImageValidationError(ValueError):
    """Raised when an image cannot be verified and fully decoded."""


FOLDER_SCHEMA = {
    "HealthyCircle": ("Healthy", 0, "circle"),
    "HealthyMeander": ("Healthy", 0, "meander"),
    "HealthySpiral": ("Healthy", 0, "spiral"),
    "PatientCircle": ("Parkinson", 1, "circle"),
    "PatientMeander": ("Parkinson", 1, "meander"),
    "PatientSpiral": ("Parkinson", 1, "spiral"),
}

# The source archive contains mea1, mea2, mea3, and mea5 for P08. The official
# page describes four meander attempts per subject, so mea5 is represented as
# logical attempt 4 while preserving the original filename and token.
KNOWN_DRAWING_INDEX_OVERRIDES = {
    ("PatientMeander", "mea5-p8.jpg"): (
        4,
        "non_standard_index_mea5_mapped_to_4",
    )
}


@dataclass(frozen=True)
class ImageRecord:
    filepath: str
    filename: str
    raw_filename: str
    raw_stem: str
    raw_subject_token: str
    class_name: str
    label: int
    drawing_type: str
    drawing_index: int
    raw_subject_id: str
    subject_id: str
    width: int
    height: int
    channels: int
    checksum_sha256: str
    perceptual_dhash: str
    file_size_bytes: int
    anomaly_flags: str

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_subject_id(raw_id: str) -> str:
    """Normalize a subject ID such as ``H1`` to ``H01``."""
    match = re.fullmatch(r"([HhPp])(\d+)", raw_id.strip())
    if not match:
        return raw_id.strip().upper()
    prefix, number = match.groups()
    return f"{prefix.upper()}{int(number):02d}"


def compute_sha256(filepath: str | Path) -> str:
    """Return the SHA-256 checksum of a file."""
    digest = hashlib.sha256()
    with Path(filepath).open("rb") as file_handle:
        for block in iter(lambda: file_handle.read(65_536), b""):
            digest.update(block)
    return digest.hexdigest()


def _perceptual_dhash(image: Image.Image, hash_size: int) -> str:
    """Compute a deterministic difference hash for near-duplicate screening."""
    if hash_size < 4 or hash_size > 32:
        raise ValueError("dHash size must be between 4 and 32")

    grayscale = image.convert("L").resize(
        (hash_size + 1, hash_size),
        Image.Resampling.LANCZOS,
    )
    pixels = grayscale.tobytes()
    hash_value = 0
    for row in range(hash_size):
        offset = row * (hash_size + 1)
        for column in range(hash_size):
            hash_value <<= 1
            hash_value |= pixels[offset + column] > pixels[offset + column + 1]

    hex_width = (hash_size * hash_size + 3) // 4
    return f"{hash_value:0{hex_width}x}"


def inspect_image(
    filepath: str | Path, dhash_size: int = 8
) -> tuple[int, int, int, str]:
    """Verify, fully decode, and inspect an image.

    Pillow's initial ``Image.open`` is lazy. Calling ``verify`` and then
    reopening the file for ``load`` prevents truncated files with readable
    headers from being accepted as valid images.
    """
    path = Path(filepath)
    try:
        with Image.open(path) as image:
            image.verify()

        with Image.open(path) as image:
            image.load()
            width, height = image.size
            channels = len(image.getbands())
            perceptual_hash = _perceptual_dhash(image, dhash_size)
    except (OSError, SyntaxError, UnidentifiedImageError, ValueError) as error:
        raise ImageValidationError(f"Image validation failed: {error}") from error

    if width <= 0 or height <= 0 or channels <= 0:
        raise ImageValidationError("Image dimensions and channels must be positive")

    return width, height, channels, perceptual_hash


def _parse_filename(
    filename: str,
    parent_dir: str,
    drawing_type: str,
) -> tuple[int, str, list[str]]:
    stem = Path(filename).stem
    anomalies: list[str] = []

    if drawing_type == "circle":
        match = re.fullmatch(r"circA-([HhPp]\d+)", stem, re.IGNORECASE)
        drawing_index = 1
    else:
        prefix = "mea" if drawing_type == "meander" else "sp"
        match = re.fullmatch(
            rf"{prefix}(\d+)-([HhPp]\d+)",
            stem,
            re.IGNORECASE,
        )
        drawing_index = int(match.group(1)) if match else 0

    if not match:
        raise MetadataParseError(
            f"Filename {filename!r} does not match the {drawing_type} schema"
        )

    raw_subject_token = match.group(1) if drawing_type == "circle" else match.group(2)
    override = KNOWN_DRAWING_INDEX_OVERRIDES.get((parent_dir, filename.lower()))
    if override:
        drawing_index, anomaly = override
        anomalies.append(anomaly)
    elif drawing_index not in range(1, 5):
        raise MetadataParseError(
            f"Drawing index {drawing_index} is outside the supported range 1..4"
        )

    return drawing_index, raw_subject_token, anomalies


def parse_newhandpd_file(
    filepath: str | Path,
    root_dir: str | Path,
    *,
    dhash_size: int = 8,
) -> ImageRecord:
    """Parse and fully validate one image from the NewHandPD directory."""
    path = Path(filepath).resolve()
    root = Path(root_dir).resolve()
    try:
        relative_path = path.relative_to(root)
    except ValueError as error:
        raise MetadataParseError(f"{path} is outside dataset root {root}") from error

    parent_dir = path.parent.name
    try:
        class_name, label, drawing_type = FOLDER_SCHEMA[parent_dir]
    except KeyError as error:
        raise MetadataParseError(f"Unknown NewHandPD folder: {parent_dir!r}") from error

    drawing_index, raw_subject_token, anomalies = _parse_filename(
        path.name,
        parent_dir,
        drawing_type,
    )

    if any(character.islower() for character in raw_subject_token):
        anomalies.append("lowercase_subject_token")

    expected_prefix = "H" if label == 0 else "P"
    source_prefix = raw_subject_token[0].upper()
    if source_prefix != expected_prefix:
        anomalies.append(
            "folder_class_mismatch_p_token_in_healthy_folder"
            if label == 0
            else "folder_class_mismatch_h_token_in_patient_folder"
        )

    subject_number = re.search(r"\d+", raw_subject_token)
    if subject_number is None:
        raise MetadataParseError(f"Missing subject number in {path.name!r}")

    raw_subject_id = f"{expected_prefix}{subject_number.group()}"
    width, height, channels, perceptual_hash = inspect_image(path, dhash_size)

    return ImageRecord(
        filepath=relative_path.as_posix(),
        filename=path.name,
        raw_filename=path.name,
        raw_stem=path.stem,
        raw_subject_token=raw_subject_token,
        class_name=class_name,
        label=label,
        drawing_type=drawing_type,
        drawing_index=drawing_index,
        raw_subject_id=raw_subject_id,
        subject_id=normalize_subject_id(raw_subject_id),
        width=width,
        height=height,
        channels=channels,
        checksum_sha256=compute_sha256(path),
        perceptual_dhash=perceptual_hash,
        file_size_bytes=path.stat().st_size,
        anomaly_flags=",".join(anomalies) if anomalies else "none",
    )
