"""Leakage-safe dataset splits for ParkinDraw.

Pembagian dilakukan pada level subjek, bukan gambar. Assignment yang sama
dipakai untuk Circle, Meander, dan Spiral agar fusion tetap sah.

Dua tahap:

1. holdout terkunci --- dipisahkan sekali, tidak disentuh selama tuning;
2. Stratified Group K-Fold pada development set untuk Optuna.
"""

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, train_test_split

from parkindraw.data.dataset import build_manifest

DEFAULT_SEED = 42
DEFAULT_HOLDOUT_SIZE = 0.2
DEFAULT_N_SPLITS = 3

DRAWING_TYPES = ("circle", "meander", "spiral")


class SplitError(RuntimeError):
    """Raised when a produced split violates a leakage guarantee."""


def subject_table(manifest: pd.DataFrame) -> pd.DataFrame:
    """Satu baris per subjek, dengan class dan label-nya."""
    subjects = (
        manifest[["subject_id", "class_name", "label"]]
        .drop_duplicates()
        .sort_values("subject_id", ignore_index=True)
    )
    ganda = subjects["subject_id"].duplicated().sum()
    if ganda:
        raise SplitError(f"{ganda} subject_id memiliki lebih dari satu class")
    return subjects


def build_holdout(
    manifest: pd.DataFrame,
    *,
    holdout_size: float = DEFAULT_HOLDOUT_SIZE,
    seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    """Pisahkan sebagian subjek sebagai test set terkunci.

    Stratifikasi menjaga proporsi Healthy/Parkinson; pemisahan pada level
    subjek menjaga seluruh gambar milik satu orang tetap menyatu.
    """
    subjects = subject_table(manifest)
    dev, holdout = train_test_split(
        subjects,
        test_size=holdout_size,
        stratify=subjects["label"],
        random_state=seed,
    )
    subjects = subjects.copy()
    subjects["partition"] = "development"
    subjects.loc[subjects["subject_id"].isin(holdout["subject_id"]), "partition"] = (
        "holdout"
    )
    return subjects.sort_values("subject_id", ignore_index=True)


def build_folds(
    manifest: pd.DataFrame,
    development_subjects: pd.Series,
    *,
    n_splits: int = DEFAULT_N_SPLITS,
    seed: int = DEFAULT_SEED,
) -> list[pd.DataFrame]:
    """Bagi development set menjadi fold train/validation per subjek.

    StratifiedGroupKFold dijalankan pada seluruh gambar development dengan
    `groups=subject_id`, sehingga assignment yang dihasilkan identik untuk
    ketiga drawing type.
    """
    dev = manifest[manifest["subject_id"].isin(development_subjects)]
    splitter = StratifiedGroupKFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=seed,
    )

    folds: list[pd.DataFrame] = []
    for train_idx, val_idx in splitter.split(
        dev, dev["label"], groups=dev["subject_id"]
    ):
        val_subjects = set(dev.iloc[val_idx]["subject_id"])
        train_subjects = set(dev.iloc[train_idx]["subject_id"])
        bocor = train_subjects & val_subjects
        if bocor:
            raise SplitError(f"Subjek muncul di train dan validation: {sorted(bocor)}")

        assignment = subject_table(dev).copy()
        assignment["split"] = assignment["subject_id"].map(
            lambda s: "validation" if s in val_subjects else "train"
        )
        folds.append(assignment.sort_values("subject_id", ignore_index=True))
    return folds


def build_sessions(manifest: pd.DataFrame, subjects: pd.Series) -> pd.DataFrame:
    """Bentuk empat application-matched session untuk setiap subjek.

    Aplikasi meminta satu Circle, satu Meander, dan satu Spiral. Circle
    digunakan ulang karena dataset hanya menyediakan satu per subjek.
    """
    subset = manifest[manifest["subject_id"].isin(subjects)]
    baris = []
    for subject_id, group in subset.groupby("subject_id", sort=True):
        per_type = {
            drawing: group[group["drawing_type"] == drawing].set_index("drawing_index")
            for drawing in DRAWING_TYPES
        }
        circle = per_type["circle"]
        if len(circle) != 1:
            raise SplitError(f"{subject_id} tidak memiliki tepat satu circle")

        for index in range(1, 5):
            baris.append(
                {
                    "session_id": f"{subject_id}-S{index}",
                    "subject_id": subject_id,
                    "class_name": group["class_name"].iloc[0],
                    "label": int(group["label"].iloc[0]),
                    "circle": circle.iloc[0]["filepath"],
                    "meander": per_type["meander"].loc[index, "filepath"],
                    "spiral": per_type["spiral"].loc[index, "filepath"],
                }
            )
    return pd.DataFrame(baris)


def verify_no_leakage(holdout: pd.DataFrame, folds: list[pd.DataFrame]) -> None:
    """Pastikan holdout tidak pernah muncul di fold mana pun."""
    terkunci = set(holdout.loc[holdout["partition"] == "holdout", "subject_id"])
    for nomor, fold in enumerate(folds):
        bocor = terkunci & set(fold["subject_id"])
        if bocor:
            raise SplitError(f"Subjek holdout muncul di fold_{nomor}: {sorted(bocor)}")


def write_splits(
    output_dir: str | Path,
    holdout: pd.DataFrame,
    folds: list[pd.DataFrame],
    sessions: pd.DataFrame,
    metadata: dict,
) -> None:
    """Tulis manifest split secara deterministik."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    holdout.to_csv(out / "holdout.csv", index=False, lineterminator="\n")
    for nomor, fold in enumerate(folds):
        fold.to_csv(out / f"fold_{nomor}.csv", index=False, lineterminator="\n")
    sessions.to_csv(out / "sessions.csv", index=False, lineterminator="\n")
    (out / "split_config.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def run_split(
    raw_dir: str | Path = "data/raw",
    output_dir: str | Path = "data/splits",
    *,
    holdout_size: float = DEFAULT_HOLDOUT_SIZE,
    n_splits: int = DEFAULT_N_SPLITS,
    seed: int = DEFAULT_SEED,
) -> dict:
    """Bangun seluruh manifest split dan kembalikan ringkasannya."""
    manifest = build_manifest(raw_dir)

    holdout = build_holdout(manifest, holdout_size=holdout_size, seed=seed)
    development = holdout.loc[holdout["partition"] == "development", "subject_id"]
    locked = holdout.loc[holdout["partition"] == "holdout", "subject_id"]

    folds = build_folds(manifest, development, n_splits=n_splits, seed=seed)
    verify_no_leakage(holdout, folds)
    sessions = build_sessions(manifest, locked)

    ringkasan = {
        "seed": seed,
        "holdout_size": holdout_size,
        "n_splits": n_splits,
        "total_images": len(manifest),
        "total_subjects": len(holdout),
        "holdout_subjects": int((holdout["partition"] == "holdout").sum()),
        "development_subjects": int((holdout["partition"] == "development").sum()),
        "holdout_class_counts": holdout.loc[holdout["partition"] == "holdout"]
        .groupby("class_name")
        .size()
        .to_dict(),
        "development_class_counts": holdout.loc[holdout["partition"] == "development"]
        .groupby("class_name")
        .size()
        .to_dict(),
        "sessions": len(sessions),
        "fold_validation_subjects": [
            int((fold["split"] == "validation").sum()) for fold in folds
        ],
    }

    write_splits(output_dir, holdout, folds, sessions, ringkasan)
    return ringkasan


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bangun manifest split yang aman dari subject leakage.",
    )
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--output-dir", default="data/splits")
    parser.add_argument("--holdout-size", type=float, default=DEFAULT_HOLDOUT_SIZE)
    parser.add_argument("--n-splits", type=int, default=DEFAULT_N_SPLITS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    ringkasan = run_split(
        args.raw_dir,
        args.output_dir,
        holdout_size=args.holdout_size,
        n_splits=args.n_splits,
        seed=args.seed,
    )
    print(
        f"Split selesai: {ringkasan['total_subjects']} subjek "
        f"({ringkasan['development_subjects']} development, "
        f"{ringkasan['holdout_subjects']} holdout), "
        f"{ringkasan['n_splits']} fold, "
        f"{ringkasan['sessions']} session."
    )
    print(f"Artifact: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
