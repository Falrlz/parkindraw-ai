"""Leakage-safe dataset splits for ParkinDraw.

Splitting happens at the subject/cluster level rather than the image level, and
the assignment is unified across Circle, Meander, and Spiral so late fusion
stays valid.

Outputs 3 master artifacts:
1. `master_manifest.csv`: Enriched manifest with hashes, clusters, partitions, and folds.
2. `sessions.csv`: Triplet evaluation units (1 Circle + 1 Meander + 1 Spiral) for holdout.
3. `split_config.json`: Configuration and duplicate cluster audit log.
"""

import json
from collections.abc import Mapping
from pathlib import Path

import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, train_test_split

from parkindraw.data.hashing import (
    NO_CLUSTERS,
    Clusters,
    build_clusters,
    cluster_ids,
    hash_images,
)
from parkindraw.data.manifest import build_manifest

DEFAULT_SEED = 42
DEFAULT_HOLDOUT_SIZE = 0.2
DEFAULT_N_SPLITS = 3

DRAWING_TYPES = ("circle", "meander", "spiral")
SESSIONS_PER_SUBJECT = 4


class SplitError(RuntimeError):
    """Raised when a produced split violates a leakage guarantee."""


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


def build_master_manifest(
    manifest: pd.DataFrame,
    hashes: pd.Series,
    clusters: Clusters,
    holdout: pd.DataFrame,
    folds: list[pd.DataFrame],
) -> pd.DataFrame:
    """Consolidate manifest, hashes, clusters, partitions, and fold assignments into one table."""
    master = manifest.copy()
    master["image_hash"] = hashes.values
    master["cluster_id"] = cluster_ids(master["subject_id"], clusters).values

    holdout_map = dict(zip(holdout["subject_id"], holdout["partition"]))
    master["partition"] = master["subject_id"].map(holdout_map)

    for number, fold in enumerate(folds):
        fold_map = dict(zip(fold["subject_id"], fold["split"]))
        master[f"fold_{number}"] = master["subject_id"].map(fold_map)

    return master


def write_splits(
    output_dir: str | Path,
    master_manifest: pd.DataFrame,
    sessions: pd.DataFrame,
    metadata: dict,
) -> None:
    """Write the 3 unified split manifests."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    master_manifest.to_csv(
        out / "master_manifest.csv", index=False, lineterminator="\n"
    )
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

    master_manifest = build_master_manifest(
        manifest, hashes, clusters, holdout, folds
    )
    summary = _summarise(manifest, holdout, folds, sessions, clusters, config)
    write_splits(output_dir, master_manifest, sessions, summary)
    return summary
