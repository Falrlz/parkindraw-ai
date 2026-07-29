"""
Metadata data models and parsing utilities for NewHandPD dataset.
"""

from dataclasses import asdict, dataclass
import hashlib
import os
import re
from typing import Dict, Optional, Tuple
from PIL import Image


@dataclass
class ImageRecord:
    filepath: str
    filename: str
    class_name: str  # 'Healthy' or 'Parkinson'
    label: int  # 0 for Healthy, 1 for Parkinson
    drawing_type: str  # 'circle', 'meander', 'spiral'
    drawing_index: int  # 1..4
    raw_subject_id: str  # e.g., 'H1', 'P1'
    subject_id: str  # Normalized e.g., 'H01', 'P01'
    width: int
    height: int
    channels: int
    checksum_sha256: str
    file_size_bytes: int

    def to_dict(self) -> Dict:
        return asdict(self)


def normalize_subject_id(raw_id: str) -> str:
    """
    Normalizes raw subject ID like H1 -> H01, P2 -> P02, P27 -> P27.
    """
    raw_id = raw_id.upper().strip()
    match = re.match(r"^([HPhp])(\d+)$", raw_id)
    if match:
        prefix, num = match.groups()
        return f"{prefix.upper()}{int(num):02d}"
    return raw_id


def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def parse_newhandpd_file(
    filepath: str, root_dir: str
) -> Optional[ImageRecord]:
    """
    Parses a single NewHandPD file and returns an ImageRecord.
    """
    rel_path = os.path.relpath(filepath, root_dir).replace("\\", "/")
    filename = os.path.basename(filepath)
    parent_dir = os.path.basename(os.path.dirname(filepath))

    # Determine class from top-level directory (Healthy vs Patient/Parkinson)
    if parent_dir.startswith("Healthy"):
        class_name = "Healthy"
        label = 0
    elif parent_dir.startswith("Patient"):
        class_name = "Parkinson"
        label = 1
    else:
        raise ValueError(f"Unknown folder class structure: {parent_dir}")

    # Determine drawing type from folder name
    parent_lower = parent_dir.lower()
    if "circle" in parent_lower:
        drawing_type = "circle"
    elif "meander" in parent_lower:
        drawing_type = "meander"
    elif "spiral" in parent_lower:
        drawing_type = "spiral"
    else:
        raise ValueError(f"Unknown drawing type in folder: {parent_dir}")

    # Parse drawing index and subject ID from filename
    # Patterns:
    # Circle: circA-P1.jpg or circA-p27.jpg or circA-H1.jpg
    # Meander: mea1-H1.jpg, mea2-P10.jpg
    # Spiral: sp1-H1.jpg, sp3-P25.jpg
    stem = os.path.splitext(filename)[0]

    drawing_index = 1
    raw_sub_id = ""

    if drawing_type == "circle":
        drawing_index = 1
        # Match pattern after dash, e.g. circA-P1 -> P1, circA-p27 -> P27
        match = re.search(r"-([HPhp]\d+)$", stem)
        if match:
            raw_sub_id = match.group(1)
        else:
            # Fallback pattern
            match = re.search(r"([HPhp]\d+)", stem)
            if match:
                raw_sub_id = match.group(1)
    else: # meander or spiral
        # Pattern e.g. mea1-H1, sp3-P25
        match = re.search(r"^(mea|sp)(\d+)-([HPhp]\d+)$", stem, re.IGNORECASE)
        if match:
            _, idx_str, sub_str = match.groups()
            drawing_index = int(idx_str)
            raw_sub_id = sub_str
        else:
            # Fallback
            match_idx = re.search(r"^(mea|sp)(\d+)", stem, re.IGNORECASE)
            if match_idx:
                drawing_index = int(match_idx.group(2))
            match_sub = re.search(r"-([HPhp]\d+)$", stem)
            if match_sub:
                raw_sub_id = match_sub.group(1)

    if not raw_sub_id:
        # Fallback to class prefix + number if present
        prefix_char = "H" if label == 0 else "P"
        match_num = re.search(r"\d+", stem)
        if match_num:
            raw_sub_id = f"{prefix_char}{match_num.group(0)}"
        else:
            raise ValueError(f"Could not parse subject ID from {filename}")

    # Override prefix in raw_sub_id to match actual class (Healthy -> H, Parkinson -> P)
    # to fix inconsistency where HealthyCircle has circA-P.. names
    num_part = re.search(r"\d+", raw_sub_id)
    if num_part:
        prefix_char = "H" if label == 0 else "P"
        raw_sub_id = f"{prefix_char}{num_part.group(0)}"

    norm_sub_id = normalize_subject_id(raw_sub_id)

    # Compute hash and image info
    checksum = compute_sha256(filepath)
    file_size = os.path.getsize(filepath)

    with Image.open(filepath) as img:
        width, height = img.size
        # Extract channels
        if img.mode == "RGB":
            channels = 3
        elif img.mode == "L":
            channels = 1
        elif img.mode == "RGBA":
            channels = 4
        else:
            channels = len(img.getbands())

    return ImageRecord(
        filepath=rel_path,
        filename=filename,
        class_name=class_name,
        label=label,
        drawing_type=drawing_type,
        drawing_index=drawing_index,
        raw_subject_id=raw_sub_id,
        subject_id=norm_sub_id,
        width=width,
        height=height,
        channels=channels,
        checksum_sha256=checksum,
        file_size_bytes=file_size,
    )
