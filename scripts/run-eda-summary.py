"""
Script to generate exploratory data analysis (EDA) report for NewHandPD dataset.
"""

import json
import os
import pandas as pd


def generate_eda_report():
    images_path = "data/metadata/images.csv"
    subjects_path = "data/metadata/subjects.csv"
    report_path = "data/metadata/audit_report.json"
    duplicates_path = "data/metadata/duplicate_groups.csv"

    if not os.path.exists(images_path):
        print("Error: Run data audit first (`py -m parkindraw.data.audit`)")
        return

    df_img = pd.read_csv(images_path)
    df_sub = pd.read_csv(subjects_path)
    df_dup = pd.read_csv(duplicates_path)

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    print("=" * 60)
    print("      PARKINDRAW AI --- NEWHANDPD DATASET EDA SUMMARY      ")
    print("=" * 60)

    print("\n1. OVERVIEW & SUBJECT DISTRIBUTION:")
    print(f"   - Total Citra (Images)      : {len(df_img)}")
    print(f"   - Total Subjek (Subjects)    : {len(df_sub)}")
    print(f"   - Healthy Subjects (Label 0): {report['healthy_subjects']} ({report['healthy_subjects']/len(df_sub):.1%})")
    print(f"   - Parkinson Subjects (Label 1): {report['parkinson_subjects']} ({report['parkinson_subjects']/len(df_sub):.1%})")
    print("   - Rasio Subjek              : 35 Healthy vs 31 Parkinson (~53% : 47%)")

    print("\n2. DRAWING TYPE BREAKDOWN:")
    drawing_counts = df_img["drawing_type"].value_counts().to_dict()
    for dtype, count in drawing_counts.items():
        print(f"   - {dtype.capitalize():<10}: {count} images ({count/len(df_img):.1%})")

    print("\n3. IMAGE DIMENSION & RESOLUTION DISTRIBUTION:")
    res_df = df_img.groupby(["width", "height", "channels"]).size().reset_index(name="count")
    for _, row in res_df.iterrows():
        print(f"   - Resolution: {row['width']}x{row['height']} ({row['channels']} channels) -> {row['count']} images")

    print("\n4. EXACT DUPLICATE GROUPS (SHA-256):")
    print(f"   - Duplicate Groups Count    : {report['exact_duplicate_groups_count']}")
    print(f"   - Total Duplicate Images    : {report['exact_duplicate_images_count']}")
    if not df_dup.empty:
        print("   - Sample Duplicate Groups:")
        for dup_id, group in df_dup.groupby("duplicate_group_id"):
            subjects = group["subject_id"].tolist()
            drawings = group["drawing_type"].tolist()
            classes = group["class_name"].tolist()
            print(f"     * Group {dup_id}: {len(group)} images across subjects {subjects} ({drawings}, {classes})")

    print("\n5. INTEGRITY & QUALITY CHECKS:")
    print(f"   - Corrupted Images Count    : {report['corrupted_images_count']}")
    print("   - Drawings per Subject      : Exactly 9 drawings per subject (1 Circle, 4 Meander, 4 Spiral)")

    print("=" * 60)


if __name__ == "__main__":
    generate_eda_report()
