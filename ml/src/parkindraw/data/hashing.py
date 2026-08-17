"""Duplicate detection and subject clustering via content hashing.

This module computes SHA-256 hashes of image files and clusters subjects that
share byte-identical images using a Disjoint-Set Union (Union-Find) structure.
"""

import hashlib
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

import pandas as pd

# Maps a subject ID to the ID of the cluster it belongs to.
Clusters = Mapping[str, str]

# Explicit default: every subject stands alone, no duplicates known.
NO_CLUSTERS: Clusters = MappingProxyType({})


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
