"""Dataset loading for the NewHandPD static-image subset.

Label dan drawing type diambil dari nama folder. Subject ID dan drawing index
di-parse dari nama file. File asli tidak pernah diubah.
"""

import re
from pathlib import Path

import pandas as pd

# Folder menentukan class dan drawing type. Nama file tidak pernah menentukan
# class, karena seluruh circle memakai prefix "P" sebagai indeks partisipan
# di kedua folder (HealthyCircle/circA-P1.jpg dan PatientCircle/circA-P1.jpg).
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

# Arsip sumber memiliki mea1, mea2, mea3, dan mea5 untuk subjek P08.
# Protokol dataset menetapkan empat meander, jadi mea5 dipetakan ke index 4.
DRAWING_INDEX_OVERRIDES = {("PatientMeander", "mea5-p8"): 4}

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
        raise ManifestError(f"Nama file tidak sesuai skema {drawing_type}: {path.name}")

    if drawing_type == "circle":
        drawing_index, subject_number = 1, match.group(1)
    else:
        drawing_index, subject_number = int(match.group(1)), match.group(2)

    override = DRAWING_INDEX_OVERRIDES.get((folder, stem.lower()))
    if override is not None:
        drawing_index = override
    elif drawing_index not in range(1, 5):
        raise ManifestError(f"Drawing index {drawing_index} di luar 1..4: {path.name}")

    # Subject ID mengikuti class dari folder, bukan prefix pada nama file.
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
    """Pindai `raw_dir` dan kembalikan satu baris per gambar.

    Urutan baris deterministik agar split dengan seed yang sama selalu
    menghasilkan pembagian yang identik.
    """
    root = Path(raw_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"Folder dataset tidak ditemukan: {root}")

    rows = []
    for folder in sorted(FOLDER_SCHEMA):
        folder_path = root / folder
        if not folder_path.is_dir():
            raise FileNotFoundError(f"Folder wajib tidak ditemukan: {folder_path}")
        for path in sorted(folder_path.iterdir(), key=lambda p: p.name.casefold()):
            if path.is_file() and path.suffix.lower() in extensions:
                rows.append(_parse_file(path, folder))

    manifest = pd.DataFrame(rows, columns=MANIFEST_COLUMNS)
    return manifest.sort_values(
        ["drawing_type", "subject_id", "drawing_index"],
        ignore_index=True,
    )


def filter_drawing(manifest: pd.DataFrame, drawing_type: str) -> pd.DataFrame:
    """Ambil subset satu drawing type untuk melatih satu model."""
    if drawing_type not in {"circle", "meander", "spiral"}:
        raise ValueError(f"Drawing type tidak dikenal: {drawing_type}")
    return manifest.loc[manifest["drawing_type"] == drawing_type].reset_index(drop=True)


class DrawingDataset:
    """PyTorch Dataset yang membaca gambar berdasarkan manifest.

    Torch di-import saat instansiasi agar modul ini tetap dapat dipakai untuk
    membangun manifest tanpa dependency training terpasang.
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
