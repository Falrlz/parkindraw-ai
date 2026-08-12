"""Metadata-only baseline for ParkinDraw.

EDA found that non-clinical image metadata separates the classes strongly on
its own -- file size reaches a univariate AUC of 0.87 for spirals. A classifier
fed nothing but width, height, aspect ratio and file size can therefore score
well without ever looking at the handwriting.

This module measures exactly how well. The resulting number is a mandatory
reference point: a ResNet-18 score is only evidence of clinical learning if it
clearly exceeds this baseline. Reporting the model alone would be misleading.

The baseline deliberately mirrors the real evaluation protocol -- same folds,
same subject-level aggregation, same metric -- so the two numbers are directly
comparable.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from parkindraw.data.dataset import build_manifest
from parkindraw.evaluation.metrics import aggregate_by_subject

DRAWING_TYPES = ("circle", "meander", "spiral")

# Purely non-clinical properties: none of them describes the drawn stroke.
FEATURES = ("width", "height", "aspect_ratio", "file_size_kb")

DEFAULT_SEED = 42
DEFAULT_N_SPLITS = 3

# Grayscale value below which a pixel counts as ink. Matches the EDA notebook.
INK_THRESHOLD = 200


class BaselineError(RuntimeError):
    """Raised when the baseline cannot be evaluated as specified."""


def image_metadata(manifest: pd.DataFrame, raw_dir: str | Path) -> pd.DataFrame:
    """Attach file-level metadata to the manifest.

    Only the image header is read for the dimensions, so this stays cheap even
    though it touches every file.
    """
    root = Path(raw_dir)
    records = []
    for relative in manifest["filepath"]:
        path = root / relative
        with Image.open(path) as image:
            width, height = image.size
        records.append(
            {
                "width": width,
                "height": height,
                "aspect_ratio": width / height,
                "file_size_kb": path.stat().st_size / 1024.0,
            }
        )
    return pd.concat([manifest.reset_index(drop=True), pd.DataFrame(records)], axis=1)


def evaluate_fold(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    *,
    seed: int = DEFAULT_SEED,
) -> float:
    """Fit on the training subjects and return subject-level ROC-AUC."""
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, random_state=seed),
    )
    model.fit(train[list(FEATURES)], train["label"])

    probabilities = model.predict_proba(validation[list(FEATURES)])[:, 1]
    # Shared with the model evaluation on purpose: both numbers are only
    # comparable while they are aggregated the same way.
    subjects = aggregate_by_subject(
        validation["subject_id"].tolist(),
        validation["label"].tolist(),
        probabilities,
    )

    if subjects["label"].nunique() < 2:
        raise BaselineError("Validation fold contains a single class")
    return float(roc_auc_score(subjects["label"], subjects["probability"]))


def evaluate_drawing(
    features: pd.DataFrame,
    folds: list[pd.DataFrame],
    drawing_type: str,
    *,
    seed: int = DEFAULT_SEED,
) -> dict:
    """Evaluate one drawing type across every fold."""
    subset = features[features["drawing_type"] == drawing_type]

    scores = []
    for number, fold in enumerate(folds):
        assignment = dict(zip(fold["subject_id"], fold["split"]))
        side = subset["subject_id"].map(assignment)

        train = subset[side == "train"]
        validation = subset[side == "validation"]
        if train.empty or validation.empty:
            raise BaselineError(f"{drawing_type}: fold_{number} has an empty side")

        scores.append(evaluate_fold(train, validation, seed=seed))

    return {
        "fold_auc": [round(score, 4) for score in scores],
        "mean_auc": round(float(np.mean(scores)), 4),
        "std_auc": round(float(np.std(scores)), 4),
        "images": int(len(subset)),
        "subjects": int(subset["subject_id"].nunique()),
    }


def ink_fraction(filepath: str, raw_dir: str | Path) -> float:
    """Fraction of dark pixels -- a cheap proxy for how much was drawn."""
    with Image.open(Path(raw_dir) / filepath) as image:
        pixels = np.asarray(image.convert("L"))
    return float((pixels < INK_THRESHOLD).mean())


def _correlation(left: pd.Series, right: pd.Series) -> float | None:
    """Pearson correlation, or None when one side has no variance.

    A constant feature makes the correlation undefined. Returning None keeps
    the report valid JSON, which NaN would not be.
    """
    if left.nunique() < 2 or right.nunique() < 2:
        return None
    return round(float(left.corr(right)), 3)


def diagnose(features: pd.DataFrame, raw_dir: str | Path) -> dict:
    """Explain *why* the metadata separates the classes, per drawing type.

    A high baseline alone is ambiguous. File size can grow for two very
    different reasons:

    - the image is simply larger in pixels, which is a pure acquisition
      artifact and disappears once every image is resized to 224x224;
    - the drawing contains more ink, which compresses worse. Tremor produces
      longer, jagged, overlapping strokes, so this route is clinically
      plausible rather than spurious.

    Correlating file size against both explanations separates them. The result
    decides how the baseline should be read, so it is recorded alongside it.
    """
    enriched = features.copy()
    enriched["ink"] = [ink_fraction(p, raw_dir) for p in enriched["filepath"]]
    enriched["pixel_count"] = enriched["width"] * enriched["height"]

    report = {}
    for drawing_type, group in enriched.groupby("drawing_type"):
        by_class = group.groupby("class_name")
        report[drawing_type] = {
            "file_size_vs_ink": _correlation(group["file_size_kb"], group["ink"]),
            "file_size_vs_pixel_count": _correlation(
                group["file_size_kb"], group["pixel_count"]
            ),
            "ink_vs_label": _correlation(group["ink"], group["label"]),
            "mean_file_size_kb": by_class["file_size_kb"].mean().round(1).to_dict(),
            "mean_width": by_class["width"].mean().round(1).to_dict(),
            "mean_ink": by_class["ink"].mean().round(4).to_dict(),
        }
    return report


def development_subjects(folds: list[pd.DataFrame]) -> set[str]:
    """Subjects covered by the folds, i.e. everyone except the locked holdout."""
    return set().union(*(set(fold["subject_id"]) for fold in folds))


def load_folds(
    splits_dir: str | Path, n_splits: int = DEFAULT_N_SPLITS
) -> list[pd.DataFrame]:
    """Read the cross-validation folds written by `parkindraw.data.splits`."""
    directory = Path(splits_dir)
    folds = []
    for number in range(n_splits):
        path = directory / f"fold_{number}.csv"
        if not path.is_file():
            raise FileNotFoundError(f"Fold manifest not found: {path}")
        folds.append(pd.read_csv(path))
    return folds


def run_baseline(
    raw_dir: str | Path = "data/raw",
    splits_dir: str | Path = "data/splits",
    output_path: str | Path | None = "reports/metadata_baseline.json",
    *,
    n_splits: int = DEFAULT_N_SPLITS,
    seed: int = DEFAULT_SEED,
) -> dict:
    """Measure the metadata-only baseline for every drawing type.

    The manifest is restricted to development subjects *before* any file is
    opened, so the locked holdout is never touched -- not even to read its file
    sizes.
    """
    folds = load_folds(splits_dir, n_splits)
    manifest = build_manifest(raw_dir)
    development = manifest[manifest["subject_id"].isin(development_subjects(folds))]
    features = image_metadata(development, raw_dir)

    results = {
        drawing_type: evaluate_drawing(features, folds, drawing_type, seed=seed)
        for drawing_type in DRAWING_TYPES
    }

    summary = {
        "seed": seed,
        "n_splits": n_splits,
        "features": list(FEATURES),
        "metric": "subject-level ROC-AUC",
        "results": results,
        "highest_mean_auc": max(r["mean_auc"] for r in results.values()),
        "diagnostics": diagnose(features, raw_dir),
    }

    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return summary


def build_argument_parser():
    """Compatibility wrapper for the baseline CLI now located in `scripts`."""
    from scripts.evaluate_baseline import build_argument_parser as build_parser

    return build_parser()


def main(argv: list[str] | None = None) -> int:
    """Compatibility wrapper for the baseline CLI now located in `scripts`."""
    from scripts.evaluate_baseline import main as cli_main

    return cli_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
