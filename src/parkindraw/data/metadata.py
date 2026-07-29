"""
Metadata data models and parsing utilities for NewHandPD dataset.
Includes raw token retention and anomaly detection flags.
"""

from dataclasses import asdict, dataclass
import hashlib
import os
import re
from typing import Dict, List, Optional
from PIL import Image


@dataclass
class ImageRecord:
    filepath: str
    filename: str
    raw_filename: str
    raw_stem: str
    raw_subject_token: str
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
    anomaly_flags: str  # Comma-separated list of anomaly flags

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
    Parses a single NewHandPD file and returns an ImageRecord with anomaly flags.
    """
    rel_path = os.path.relpath(filepath, root_dir).replace("\\", "/")
    filename = os.path.basename(filepath)
    stem = os.path.splitext(filename)[0]
    parent_dir = os.path.basename(os.path.dirname(filepath))

    anomalies: List[str] = []

    # Class determination from parent directory
    if parent_dir.startswith("Healthy"):
        class_name = "Healthy"
        label = 0
    elif parent_dir.startswith("Patient"):
        class_name = "Parkinson"
        label = 1
    else:
        raise ValueError(f"Unknown folder class structure: {parent_dir}")

    # Drawing type determination from parent directory
    parent_lower = parent_dir.lower()
    if "circle" in parent_lower:
        drawing_type = "circle"
    elif "meander" in parent_lower:
        drawing_type = "meander"
    elif "spiral" in parent_lower:
        drawing_type = "spiral"
    else:
        raise ValueError(f"Unknown drawing type in folder: {parent_dir}")

    drawing_index = 1
    raw_subject_token = ""

    # Specific Anomaly Handling for mea5-P8.jpg
    if filename.lower() == "mea5-p8.jpg":
        anomalies.append("non_standard_index_mea5_mapped_to_4")
        drawing_index = 4
        raw_subject_token = "P8"
    elif drawing_type == "circle":
        drawing_index = 1
        match = re.search(r"-([HPhp]\d+)$", stem)
        if match:
            raw_subject_token = match.group(1)
        else:
            match = re.search(r"([HPhp]\d+)", stem)
            if match:
                raw_subject_token = match.group(1)
    else:
        # Meander or Spiral
        match = re.search(r"^(mea|sp)(\d+)-([HPhp]\d+)$", stem, re.IGNORECASE)
        if match:
            _, idx_str, sub_str = match.groups()
            drawing_index = int(idx_str)
            raw_subject_token = sub_str
        else:
            match_idx = re.search(r"^(mea|sp)(\d+)", stem, re.IGNORECASE)
            if match_idx:
                drawing_index = int(match_idx.group(2))
            match_sub = re.search(r"-([HPhp]\d+)$", stem)
            if match_sub:
                raw_subject_token = match_sub.group(1)

    if not raw_subject_token:
        prefix_char = "H" if label == 0 else "P"
        match_num = re.search(r"\d+", stem)
        if match_num:
            raw_subject_token = f"{prefix_char}{match_num.group(0)}"
            anomalies.append("fallback_subject_id_parsing")
        else:
            raise ValueError(f"Could not parse subject ID from {filename}")

    # Flag if subject token uses lowercase 'p' or 'h'
    if any(c.islower() for c in raw_subject_token):
        anomalies.append("lowercase_subject_token")

    # Flag if folder class mismatches raw filename prefix (e.g. circA-P1 in HealthyCircle)
    num_part = re.search(r"\d+", raw_subject_token)
    extracted_num = num_part.group(0) if num_part else ""
    expected_prefix = "H" if label == 0 else "P"

    if raw_subject_token.upper().startswith("P") and label == 0:
        anomalies.append("folder_class_mismatch_p_token_in_healthy_folder")
    elif raw_subject_token.upper().startswith("H") and label == 1:
        anomalies.append("folder_class_mismatch_h_token_in_patient_folder")

    raw_subject_id = f"{expected_prefix}{extracted_num}"
    norm_subject_id = normalize_subject_id(raw_subject_id)

    # Compute hash and image info
    checksum = compute_sha256(filepath)
    file_size = os.path.getsize(filepath)

    with Image.open(filepath) as img:
        width, height = img.size
        if img.mode == "RGB":
            channels = 3
        elif img.mode == "L":
            channels = 1
        elif img.mode == "RGBA":
            channels = 4
        else:
            channels = len(img.getbands())

    anomaly_flags_str = ",".join(anomalies) if anomalies else "none"

    return ImageRecord(
        filepath=rel_path,
        filename=filename,
        raw_filename=filename,
        raw_stem=stem,
        raw_subject_token=raw_subject_token,
        class_name=class_name,
        label=label,
        drawing_type=drawing_type,
        drawing_index=drawing_index,
        raw_subject_id=raw_subject_id,
        subject_id=norm_subject_id,
        width=width,
        height=height,
        channels=channels,
        checksum_sha256=checksum,
        file_size_bytes=file_size,
        anomaly_flags=anomaly_flags_str,
    )
