"""Image content hashing and duplicate subject clustering via Union-Find."""

import hashlib
import logging
from collections.abc import Mapping
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Mapping of a subject ID to its assigned cluster root ID.
Clusters = Mapping[str, str]


def hash_images(
    manifest: pd.DataFrame, 
    raw_dir: str | Path
    ) -> pd.Series:

    """Compute SHA-256 hashes for all image files aligned with manifest rows."""
    root = Path(raw_dir)
    logger.info("Computing SHA-256 hashes for %d images from %s...", len(manifest), root)
    # Read raw bytes and calculate SHA-256 hexadecimal hash for each file.
    hashes = manifest["filepath"].map(
        lambda relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
    )
    logger.info("Completed SHA-256 hashing: %d unique hash fingerprints found.", hashes.nunique())
    return hashes


def build_clusters(
    manifest: pd.DataFrame, 
    hashes: pd.Series
    ) -> dict[str, str]:

    """Group subjects sharing byte-identical images using Disjoint-Set Union."""
    logger.info("Clustering duplicate subjects based on identical image content...")
    parent: dict[str, str] = {}

    def find(subject: str) -> str:
        # Find root cluster representative with path halving.
        parent.setdefault(subject, subject)
        while parent[subject] != subject:
            parent[subject] = parent[parent[subject]]
            subject = parent[subject]
        return subject

    def union(left: str, right: str) -> None:
        # Deterministically merge clusters using the lexicographically smaller ID.
        winner, loser = sorted((find(left), find(right)))
        parent[loser] = winner

    # Group files by hash to detect identical images shared across subjects.
    for _, group in manifest.groupby(hashes.values, sort=False):
        subjects = sorted(set(group["subject_id"]))
        # Union all subjects that share the exact same image content.
        for other in subjects[1:]:
            union(subjects[0], other)

    # Return mapping of duplicate subjects to their resolved cluster root.
    cluster_map = {subject: find(subject) for subject in sorted(parent)}
    merged_count = sum(1 for s, c in cluster_map.items() if s != c)
    logger.info(
        "Clustering complete: %d subjects mapped into %d unique clusters (%d merged).",
        len(cluster_map),
        len(set(cluster_map.values())),
        merged_count,
    )
    return cluster_map


def cluster_ids(
    subjects: pd.Series, 
    clusters: Clusters
    ) -> pd.Series:
    
    """Map subject IDs to cluster IDs, defaulting to subject ID if unclustered."""
    # Resolve each subject ID to its cluster root or keep original ID.
    return subjects.map(lambda subject: clusters.get(subject, subject))
