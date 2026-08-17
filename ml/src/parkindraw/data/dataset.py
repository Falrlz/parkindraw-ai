"""PyTorch Dataset implementation for the NewHandPD static-image subset.

Torch and PIL are imported lazily so this module stays usable on machines
without heavy training dependencies installed.
"""

from pathlib import Path

import pandas as pd

from parkindraw.data.anomalies import ManifestError
from parkindraw.data.manifest import build_manifest, filter_drawing


class DrawingDataset:
    """PyTorch Dataset that reads images according to a manifest."""

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


__all__ = [
    "DrawingDataset",
    "ManifestError",
    "build_manifest",
    "filter_drawing",
]
