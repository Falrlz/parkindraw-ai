"""
Data integrity and audit unit tests using standard unittest.
"""

import json
import os
import unittest
import pandas as pd


class TestDataAudit(unittest.TestCase):
    def setUp(self):
        self.metadata_dir = "data/metadata"

    def test_metadata_files_exist(self):
        self.assertTrue(os.path.exists(os.path.join(self.metadata_dir, "images.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.metadata_dir, "subjects.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.metadata_dir, "duplicate_groups.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.metadata_dir, "audit_report.json")))

    def test_images_metadata_integrity(self):
        images_csv = os.path.join(self.metadata_dir, "images.csv")
        df = pd.read_csv(images_csv)

        # Check total image count (NewHandPD spec: 594 images)
        self.assertEqual(len(df), 594, f"Expected 594 images, found {len(df)}")

        # Check required columns
        required_cols = [
            "filepath",
            "filename",
            "class_name",
            "label",
            "drawing_type",
            "drawing_index",
            "subject_id",
            "width",
            "height",
            "channels",
            "checksum_sha256",
        ]
        for col in required_cols:
            self.assertIn(col, df.columns, f"Missing required column {col}")

        # Check class labels (0 or 1)
        self.assertEqual(set(df["label"].unique()), {0, 1})

        # Check drawing types (circle, meander, spiral)
        self.assertEqual(set(df["drawing_type"].unique()), {"circle", "meander", "spiral"})

        # Check no missing checksums
        self.assertEqual(df["checksum_sha256"].isna().sum(), 0)

    def test_subjects_metadata_integrity(self):
        subjects_csv = os.path.join(self.metadata_dir, "subjects.csv")
        df = pd.read_csv(subjects_csv)

        # Check total subject count (NewHandPD spec: 66 subjects = 35 Healthy + 31 Parkinson)
        self.assertEqual(len(df), 66, f"Expected 66 subjects, found {len(df)}")

        healthy_count = (df["label"] == 0).sum()
        parkinson_count = (df["label"] == 1).sum()

        self.assertEqual(healthy_count, 35, f"Expected 35 Healthy subjects, found {healthy_count}")
        self.assertEqual(parkinson_count, 31, f"Expected 31 Parkinson subjects, found {parkinson_count}")

        # Check drawing counts per subject: 1 Circle, 4 Meander, 4 Spiral = 9 images per subject
        self.assertTrue((df["total_images"] == 9).all(), "Every subject should have exactly 9 drawings")

    def test_audit_report_summary(self):
        report_json = os.path.join(self.metadata_dir, "audit_report.json")
        with open(report_json, "r", encoding="utf-8") as f:
            report = json.load(f)

        self.assertEqual(report["total_images"], 594)
        self.assertEqual(report["total_subjects"], 66)
        self.assertEqual(report["healthy_subjects"], 35)
        self.assertEqual(report["parkinson_subjects"], 31)
        self.assertEqual(report["corrupted_images_count"], 0)


if __name__ == "__main__":
    unittest.main()
