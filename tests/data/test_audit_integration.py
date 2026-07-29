"""
Integration tests for data audit engine using a temporary dataset directory.
"""

import json
import os
import shutil
import tempfile
import unittest
from PIL import Image
import pandas as pd

from parkindraw.data.audit import run_data_audit


class TestAuditIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.raw_dir = os.path.join(self.test_dir, "raw")
        self.meta_dir = os.path.join(self.test_dir, "metadata")

        # Create mock raw structure
        os.makedirs(os.path.join(self.raw_dir, "HealthyCircle"), exist_ok=True)
        os.makedirs(os.path.join(self.raw_dir, "HealthyMeander"), exist_ok=True)
        os.makedirs(os.path.join(self.raw_dir, "PatientSpiral"), exist_ok=True)

        # Create mock images
        img1 = Image.new("RGB", (100, 100), color="white")
        img1.save(os.path.join(self.raw_dir, "HealthyCircle", "circA-H1.jpg"))

        # Duplicate images (same content img1)
        img1.save(os.path.join(self.raw_dir, "HealthyMeander", "mea1-H1.jpg"))

        # Different image
        img2 = Image.new("RGB", (120, 120), color="black")
        img2.save(os.path.join(self.raw_dir, "PatientSpiral", "sp1-P1.jpg"))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_run_data_audit_integration(self):
        report = run_data_audit(raw_dir=self.raw_dir, output_dir=self.meta_dir)

        self.assertIsNotNone(report)
        self.assertEqual(report["total_images"], 3)
        self.assertEqual(report["total_subjects"], 2)

        # Verify artifacts written
        self.assertTrue(os.path.exists(os.path.join(self.meta_dir, "images.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.meta_dir, "subjects.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.meta_dir, "duplicate_groups.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.meta_dir, "audit_report.json")))

        df_img = pd.read_csv(os.path.join(self.meta_dir, "images.csv"))
        self.assertEqual(len(df_img), 3)
        self.assertIn("anomaly_flags", df_img.columns)

        df_dup = pd.read_csv(os.path.join(self.meta_dir, "duplicate_groups.csv"))
        self.assertEqual(len(df_dup), 2)  # img1 and its duplicate in HealthyMeander


if __name__ == "__main__":
    unittest.main()
