"""Leakage-safe dataset splitting and dynamic cross-validation folds."""

import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, train_test_split

from src.config.config import (
    DEFAULT_CV_FOLDS,
    DEFAULT_HOLDOUT_SIZE,
    DEFAULT_SEED,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SplitError(RuntimeError):
    """Raised when a split violates clinical leakage guarantees."""


def split_holdout(
    manifest: pd.DataFrame,
    *,
    holdout_size: float = DEFAULT_HOLDOUT_SIZE,
    seed: int = DEFAULT_SEED,
    ) -> pd.DataFrame:

    """Lock clinical holdout set (default: 20%) based on cluster_id and label."""
    # Ambil subjek unik beserta cluster_id dan label kelas
    subjects = (
        manifest[["subject_id", "cluster_id", "label"]]
        .drop_duplicates()
        .sort_values("cluster_id", ignore_index=True)
    )

    # Bagi subjek pada level cluster_id agar pasien kembar tidak terpisah
    cluster_table = subjects[["cluster_id", "label"]].drop_duplicates()
    _, holdout_clusters = train_test_split(
        cluster_table,
        test_size=holdout_size,
        stratify=cluster_table["label"],
        random_state=seed,
    )

    # Petakan partisi: 'holdout' atau 'development'
    is_holdout = subjects["cluster_id"].isin(holdout_clusters["cluster_id"])
    partition_map = dict(
        zip(subjects["subject_id"], ["holdout" if h else "development" for h in is_holdout])
    )

    master = manifest.copy()
    master["partition"] = master["subject_id"].map(partition_map)

    dev_subjects = master[master["partition"] == "development"]["subject_id"].nunique()
    holdout_subjects = master[master["partition"] == "holdout"]["subject_id"].nunique()
    logger.info(
        "Holdout locked: %d development, %d holdout subjects (seed=%d).",
        dev_subjects,
        holdout_subjects,
        seed,
    )
    return master


def get_cv_folds(
    master_manifest: pd.DataFrame,
    *,
    n_splits: int = DEFAULT_CV_FOLDS,
    seed: int = DEFAULT_SEED,
    ) -> list[tuple[pd.DataFrame, pd.DataFrame]]:

    """Dynamically split development partition into n_splits (train_df, val_df) folds."""
    dev_df = master_manifest[master_manifest.get("partition", "development") == "development"].copy()

    splitter = StratifiedGroupKFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=seed,
    )

    folds: list[tuple[pd.DataFrame, pd.DataFrame]] = []
    for train_idx, val_idx in splitter.split(
        dev_df, dev_df["label"], groups=dev_df["cluster_id"]
    ):
        train_df = dev_df.iloc[train_idx].reset_index(drop=True)
        val_df = dev_df.iloc[val_idx].reset_index(drop=True)

        # Verifikasi nol kebocoran subjek antar train dan validation
        overlap = set(train_df["subject_id"]) & set(val_df["subject_id"])
        if overlap:
            raise SplitError(f"Subjects leaked across dynamic fold: {sorted(overlap)}")

        folds.append((train_df, val_df))

    return folds


def verify_no_leakage(
    master_manifest: pd.DataFrame
    ) -> None:

    """Verify that identical image hashes never cross development and holdout."""
    if "partition" not in master_manifest.columns or "image_hash" not in master_manifest.columns:
        return

    partition_map = dict(zip(master_manifest["subject_id"], master_manifest["partition"]))
    sides = master_manifest["subject_id"].map(partition_map)

    for image_hash, group in sides.groupby(master_manifest["image_hash"].values):
        if group.nunique() > 1:
            offenders = master_manifest.loc[group.index, "filepath"].tolist()
            raise SplitError(
                f"Identical image ({image_hash[:12]}) spread across partitions: {offenders}"
            )
    logger.info("Zero-leakage verification passed: 100% clean isolation.")
