"""Leakage-safe dataset splits for ParkinDraw.

Splitting happens at the subject level rather than the image level, and the
same assignment is reused for Circle, Meander, and Spiral so that late fusion
of the three models stays valid.

Two stages:

1. a locked holdout, separated once and never touched during tuning;
2. Stratified Group K-Fold over the development set, used by Optuna.

The indivisible unit is not the subject but the *cluster*: this dataset ships
byte-identical images under distinct subject IDs, so subjects linked by a
duplicate are split together. Clusters are derived from file hashes at runtime
(see `build_clusters`) rather than hard-coded, and `verify_no_leakage` audits
the result against those hashes directly.
"""

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, train_test_split

from parkindraw.data.dataset import build_manifest

DEFAULT_SEED = 42
DEFAULT_HOLDOUT_SIZE = 0.2
DEFAULT_N_SPLITS = 3

DRAWING_TYPES = ("circle", "meander", "spiral")
SESSIONS_PER_SUBJECT = 4

# Maps a subject ID to the ID of the cluster it belongs to.
Clusters = Mapping[str, str]

# Explicit default: every subject stands alone, no duplicates known.
NO_CLUSTERS: Clusters = MappingProxyType({})


class SplitError(RuntimeError):
    """Raised when a produced split violates a leakage guarantee."""


def hash_images(manifest: pd.DataFrame, raw_dir: str | Path) -> pd.Series:
    """Hash the contents of every image, aligned with the manifest rows."""
    root = Path(raw_dir)
    return manifest["filepath"].map(
        lambda relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
    )


def build_clusters(manifest: pd.DataFrame, hashes: pd.Series) -> dict[str, str]:
    """Group subjects that share byte-identical images into one cluster.

    Cross-subject duplicates defeat subject-level splitting: the same file can
    land in training under one subject ID and in validation under another.

    Returns subject_id -> cluster_id for duplicated subjects only; every other
    subject is its own cluster, resolved through `cluster_ids`.
    """
    parent: dict[str, str] = {}

    def find(subject: str) -> str:
        parent.setdefault(subject, subject)
        while parent[subject] != subject:
            parent[subject] = parent[parent[subject]]
            subject = parent[subject]
        return subject

    def union(left: str, right: str) -> None:
        # The lexicographically smaller root always wins, which keeps cluster
        # IDs stable across runs regardless of manifest ordering.
        winner, loser = sorted((find(left), find(right)))
        parent[loser] = winner

    for _, group in manifest.groupby(hashes.values, sort=False):
        subjects = sorted(set(group["subject_id"]))
        for other in subjects[1:]:
            union(subjects[0], other)

    return {subject: find(subject) for subject in sorted(parent)}


def cluster_ids(subjects: pd.Series, clusters: Clusters) -> pd.Series:
    """Map subject IDs to cluster IDs; an unduplicated subject is its own."""
    return subjects.map(lambda subject: clusters.get(subject, subject))


def subject_table(manifest: pd.DataFrame) -> pd.DataFrame:
    """Return one row per subject, carrying its class name and label."""
    subjects = (
        manifest[["subject_id", "class_name", "label"]]
        .drop_duplicates()
        .sort_values("subject_id", ignore_index=True)
    )
    ambiguous = subjects["subject_id"].duplicated().sum()
    if ambiguous:
        raise SplitError(f"{ambiguous} subject_id map to more than one class")
    return subjects


def build_holdout(
    manifest: pd.DataFrame,
    clusters: Clusters = NO_CLUSTERS,
    *,
    holdout_size: float = DEFAULT_HOLDOUT_SIZE,
    seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    """Set aside a share of the subjects as a locked test set.

    Stratification preserves the Healthy/Parkinson ratio, while splitting on
    clusters keeps every image belonging to one person, or to their duplicates,
    on the same side of the boundary.
    """
    subjects = subject_table(manifest).copy()
    subjects["cluster_id"] = cluster_ids(subjects["subject_id"], clusters)

    cluster_table = (
        subjects[["cluster_id", "class_name", "label"]]
        .drop_duplicates()
        .sort_values("cluster_id", ignore_index=True)
    )

    _, holdout_clusters = train_test_split(
        cluster_table,
        test_size=holdout_size,
        stratify=cluster_table["label"],
        random_state=seed,
    )

    subjects["partition"] = "development"
    subjects.loc[
        subjects["cluster_id"].isin(holdout_clusters["cluster_id"]), "partition"
    ] = "holdout"

    return subjects.drop(columns=["cluster_id"]).sort_values(
        "subject_id", ignore_index=True
    )


def build_folds(
    manifest: pd.DataFrame,
    development_subjects: pd.Series,
    clusters: Clusters = NO_CLUSTERS,
    *,
    n_splits: int = DEFAULT_N_SPLITS,
    seed: int = DEFAULT_SEED,
) -> list[pd.DataFrame]:
    """Divide the development set into per-subject train/validation folds.

    StratifiedGroupKFold runs over all development images with
    `groups=cluster_id`, so the resulting assignment is identical across the
    three drawing types and duplicate-linked subjects are never separated.
    """
    development = manifest[manifest["subject_id"].isin(development_subjects)].copy()
    development["cluster_id"] = cluster_ids(development["subject_id"], clusters)

    splitter = StratifiedGroupKFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=seed,
    )

    folds: list[pd.DataFrame] = []
    for train_index, validation_index in splitter.split(
        development, development["label"], groups=development["cluster_id"]
    ):
        validation_subjects = set(development.iloc[validation_index]["subject_id"])
        train_subjects = set(development.iloc[train_index]["subject_id"])
        overlap = train_subjects & validation_subjects
        if overlap:
            raise SplitError(
                f"Subjects appear in both train and validation: {sorted(overlap)}"
            )

        assignment = subject_table(development).copy()
        assignment["split"] = assignment["subject_id"].map(
            lambda subject: "validation" if subject in validation_subjects else "train"
        )
        folds.append(assignment.sort_values("subject_id", ignore_index=True))
    return folds


def build_sessions(manifest: pd.DataFrame, subjects: pd.Series) -> pd.DataFrame:
    """Assemble application-matched sessions for each subject in `subjects`.

    A session mirrors one use of the application -- one Circle, one Meander,
    one Spiral -- so it is a final-evaluation unit, not a training unit, and is
    only built for holdout subjects. The Circle repeats across a subject's
    sessions because the dataset provides just one.
    """
    subset = manifest[manifest["subject_id"].isin(subjects)]
    rows = []
    for subject_id, group in subset.groupby("subject_id", sort=True):
        by_drawing = {
            drawing: group[group["drawing_type"] == drawing].set_index("drawing_index")
            for drawing in DRAWING_TYPES
        }
        circle = by_drawing["circle"]
        if len(circle) != 1:
            raise SplitError(f"{subject_id} does not have exactly one circle")

        for index in range(1, SESSIONS_PER_SUBJECT + 1):
            rows.append(
                {
                    "session_id": f"{subject_id}-S{index}",
                    "subject_id": subject_id,
                    "class_name": group["class_name"].iloc[0],
                    "label": int(group["label"].iloc[0]),
                    "circle": circle.iloc[0]["filepath"],
                    "meander": by_drawing["meander"].loc[index, "filepath"],
                    "spiral": by_drawing["spiral"].loc[index, "filepath"],
                }
            )
    return pd.DataFrame(rows)


def _assert_hash_confined(
    manifest: pd.DataFrame,
    hashes: pd.Series,
    assignment: Mapping[str, str],
    context: str,
) -> None:
    """Fail if one identical image maps to more than one side of a split."""
    sides = manifest["subject_id"].map(assignment)
    assigned = sides.notna()
    for image_hash, group in sides[assigned].groupby(hashes[assigned].values):
        if group.nunique() > 1:
            offenders = manifest.loc[group.index, "filepath"].tolist()
            raise SplitError(
                f"{context}: identical image ({image_hash[:12]}) spread across "
                f"{sorted(set(group))} -- {offenders}"
            )


def verify_no_leakage(
    manifest: pd.DataFrame,
    hashes: pd.Series,
    holdout: pd.DataFrame,
    folds: list[pd.DataFrame],
) -> None:
    """Assert the split leaks nothing, judged by actual image content.

    This check deliberately ignores the cluster map used to build the split. If
    that map were incomplete, validating against it would pass silently; hashes
    are the independent source of truth.
    """
    locked = set(holdout.loc[holdout["partition"] == "holdout", "subject_id"])
    for number, fold in enumerate(folds):
        leaked = locked & set(fold["subject_id"])
        if leaked:
            raise SplitError(
                f"Holdout subjects appear in fold_{number}: {sorted(leaked)}"
            )

    _assert_hash_confined(
        manifest,
        hashes,
        dict(zip(holdout["subject_id"], holdout["partition"])),
        "Development/holdout partition",
    )
    for number, fold in enumerate(folds):
        _assert_hash_confined(
            manifest,
            hashes,
            dict(zip(fold["subject_id"], fold["split"])),
            f"Fold {number}",
        )


def write_splits(
    output_dir: str | Path,
    holdout: pd.DataFrame,
    folds: list[pd.DataFrame],
    sessions: pd.DataFrame,
    metadata: dict,
) -> None:
    """Write the split manifests, pinning line endings and key order so an
    unchanged seed reproduces byte-identical files."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    holdout.to_csv(out / "holdout.csv", index=False, lineterminator="\n")
    for number, fold in enumerate(folds):
        fold.to_csv(out / f"fold_{number}.csv", index=False, lineterminator="\n")
    sessions.to_csv(out / "sessions.csv", index=False, lineterminator="\n")
    (out / "split_config.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _cluster_members(clusters: Clusters) -> dict[str, list[str]]:
    """Invert the subject -> cluster map into cluster -> members."""
    members: dict[str, list[str]] = {}
    for subject, cluster_id in sorted(clusters.items()):
        members.setdefault(cluster_id, []).append(subject)
    return members


def _summarise(
    manifest: pd.DataFrame,
    holdout: pd.DataFrame,
    folds: list[pd.DataFrame],
    sessions: pd.DataFrame,
    clusters: Clusters,
    config: dict,
) -> dict:
    """Describe the produced split, for `split_config.json` and the CLI."""
    is_holdout = holdout["partition"] == "holdout"

    def class_counts(mask: pd.Series) -> dict:
        return holdout.loc[mask].groupby("class_name").size().to_dict()

    return {
        **config,
        "total_images": len(manifest),
        "total_subjects": len(holdout),
        "holdout_subjects": int(is_holdout.sum()),
        "development_subjects": int((~is_holdout).sum()),
        "holdout_class_counts": class_counts(is_holdout),
        "development_class_counts": class_counts(~is_holdout),
        "sessions": len(sessions),
        # Recorded so reviewers can see which subjects were merged without
        # re-hashing the raw archive themselves.
        "duplicate_clusters": _cluster_members(clusters),
        "fold_validation_subjects": [
            int((fold["split"] == "validation").sum()) for fold in folds
        ],
    }


def run_split(
    raw_dir: str | Path = "data/raw",
    output_dir: str | Path = "data/splits",
    *,
    holdout_size: float = DEFAULT_HOLDOUT_SIZE,
    n_splits: int = DEFAULT_N_SPLITS,
    seed: int = DEFAULT_SEED,
) -> dict:
    """Build every split manifest and return a summary of the result."""
    config = {"seed": seed, "holdout_size": holdout_size, "n_splits": n_splits}
    manifest = build_manifest(raw_dir)
    hashes = hash_images(manifest, raw_dir)
    clusters = build_clusters(manifest, hashes)

    holdout = build_holdout(manifest, clusters, holdout_size=holdout_size, seed=seed)
    development = holdout.loc[holdout["partition"] == "development", "subject_id"]
    locked = holdout.loc[holdout["partition"] == "holdout", "subject_id"]

    folds = build_folds(manifest, development, clusters, n_splits=n_splits, seed=seed)
    verify_no_leakage(manifest, hashes, holdout, folds)
    sessions = build_sessions(manifest, locked)

    summary = _summarise(manifest, holdout, folds, sessions, clusters, config)
    write_splits(output_dir, holdout, folds, sessions, summary)
    return summary
