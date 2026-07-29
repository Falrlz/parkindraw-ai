"""
Dataset Audit Engine for NewHandPD.
Scans raw dataset, extracts metadata with raw tokens and anomaly flags,
detects exact duplicates deterministically, and generates metadata artifacts.
"""

from collections import defaultdict
import json
import os
from typing import Dict, List
import pandas as pd
import yaml

from parkindraw.data.metadata import parse_newhandpd_file


def run_data_audit(
    raw_dir: str = "data/raw/newhandpd", output_dir: str = "data/metadata"
) -> Dict:
    """
    Scans raw_dir deterministically, audits all images, detects duplicates, and writes artifacts.
    """
    os.makedirs(output_dir, exist_ok=True)

    records = []
    corrupted_files = []

    # Deterministic file discovery
    all_filepaths = []
    for root, _, files in os.walk(raw_dir):
        for file in sorted(files):
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                all_filepaths.append(os.path.join(root, file))

    all_filepaths.sort()

    for full_path in all_filepaths:
        try:
            record = parse_newhandpd_file(full_path, raw_dir)
            if record:
                records.append(record.to_dict())
        except Exception as e:
            corrupted_files.append({"filepath": full_path, "error": str(e)})

    # Sort records deterministically
    records.sort(
        key=lambda r: (
            r["class_name"],
            r["drawing_type"],
            r["subject_id"],
            r["drawing_index"],
            r["filename"],
        )
    )

    # Detect exact duplicates by SHA-256 with deterministic sorting
    hash_groups = defaultdict(list)
    for r in records:
        hash_groups[r["checksum_sha256"]].append(r)

    duplicate_groups_map = {}
    dup_records = []
    dup_id_counter = 1

    sorted_hashes = sorted(hash_groups.keys())

    for checksum in sorted_hashes:
        group = hash_groups[checksum]
        if len(group) > 1:
            dup_id = f"dup_{dup_id_counter:03d}"
            dup_id_counter += 1
            for r in group:
                duplicate_groups_map[r["filepath"]] = dup_id
                dup_records.append(
                    {
                        "duplicate_group_id": dup_id,
                        "filepath": r["filepath"],
                        "subject_id": r["subject_id"],
                        "class_name": r["class_name"],
                        "drawing_type": r["drawing_type"],
                        "drawing_index": r["drawing_index"],
                        "checksum_sha256": checksum,
                        "anomaly_flags": r["anomaly_flags"],
                    }
                )

    # Attach duplicate_group_id to records
    for r in records:
        r["duplicate_group_id"] = duplicate_groups_map.get(r["filepath"], "")

    # Create DataFrame for images.csv
    df_images = pd.DataFrame(records)
    images_csv_path = os.path.join(output_dir, "images.csv")
    df_images.to_csv(images_csv_path, index=False)

    # Create DataFrame for duplicate_groups.csv
    df_duplicates = pd.DataFrame(dup_records)
    duplicates_csv_path = os.path.join(output_dir, "duplicate_groups.csv")
    df_duplicates.to_csv(duplicates_csv_path, index=False)

    # Create subjects.csv summary
    subject_summary = []
    grouped_sub = df_images.groupby(["subject_id", "class_name", "label"])

    for (sub_id, class_name, label), group in grouped_sub:
        circle_count = len(group[group["drawing_type"] == "circle"])
        meander_count = len(group[group["drawing_type"] == "meander"])
        spiral_count = len(group[group["drawing_type"] == "spiral"])
        total_images = len(group)
        has_anomalies = any(f != "none" for f in group["anomaly_flags"])

        subject_summary.append(
            {
                "subject_id": sub_id,
                "class_name": class_name,
                "label": label,
                "circle_count": circle_count,
                "meander_count": meander_count,
                "spiral_count": spiral_count,
                "total_images": total_images,
                "has_anomalies": has_anomalies,
            }
        )

    df_subjects = pd.DataFrame(subject_summary).sort_values("subject_id")
    subjects_csv_path = os.path.join(output_dir, "subjects.csv")
    df_subjects.to_csv(subjects_csv_path, index=False)

    # Create audit_report.json
    total_images = len(df_images)
    total_subjects = len(df_subjects)
    healthy_subjects = len(df_subjects[df_subjects["label"] == 0])
    parkinson_subjects = len(df_subjects[df_subjects["label"] == 1])

    anomalous_records_count = (df_images["anomaly_flags"] != "none").sum()

    res_counts = df_images.groupby(["width", "height"]).size().to_dict()
    res_distribution = [
        {"width": int(w), "height": int(h), "count": int(c)}
        for (w, h), c in res_counts.items()
    ]

    report = {
        "audit_timestamp": pd.Timestamp.now().isoformat(),
        "dataset_name": "NewHandPD",
        "total_images": total_images,
        "total_subjects": total_subjects,
        "healthy_subjects": healthy_subjects,
        "parkinson_subjects": parkinson_subjects,
        "drawing_counts": {
            "circle": int((df_images["drawing_type"] == "circle").sum()),
            "meander": int((df_images["drawing_type"] == "meander").sum()),
            "spiral": int((df_images["drawing_type"] == "spiral").sum()),
        },
        "exact_duplicate_groups_count": len(
            df_duplicates["duplicate_group_id"].unique()
        )
        if not df_duplicates.empty
        else 0,
        "exact_duplicate_images_count": len(df_duplicates),
        "anomalous_records_count": int(anomalous_records_count),
        "corrupted_images_count": len(corrupted_files),
        "resolution_distribution": res_distribution,
        "corrupted_files": corrupted_files,
    }

    report_json_path = os.path.join(output_dir, "audit_report.json")
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(
        f"Audit Complete! Processed {total_images} images from {total_subjects} subjects."
    )
    print(f"Healthy Subjects: {healthy_subjects}, Parkinson Subjects: {parkinson_subjects}")
    print(f"Duplicate Groups: {report['exact_duplicate_groups_count']} (total duplicate images: {report['exact_duplicate_images_count']})")
    print(f"Anomalous Records: {anomalous_records_count}")
    print(f"Metadata artifacts saved to: {output_dir}")

    return report


def main():
    config_path = "configs/data/audit.yaml"
    raw_dir = "data/raw/newhandpd"
    output_dir = "data/metadata"

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            raw_dir = cfg.get("raw_data_dir", raw_dir)
            output_dir = cfg.get("metadata_output_dir", output_dir)

    run_data_audit(raw_dir=raw_dir, output_dir=output_dir)


if __name__ == "__main__":
    main()
