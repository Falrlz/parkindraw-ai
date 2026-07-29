"""
Unit tests for metadata parsing and anomaly handling.
"""

import os
import unittest
from parkindraw.data.metadata import normalize_subject_id, parse_newhandpd_file


class TestMetadataParsing(unittest.TestCase):
    def setUp(self):
        self.raw_dir = "data/raw/newhandpd"

    def test_normalize_subject_id(self):
        self.assertEqual(normalize_subject_id("H1"), "H01")
        self.assertEqual(normalize_subject_id("h1"), "H01")
        self.assertEqual(normalize_subject_id("P2"), "P02")
        self.assertEqual(normalize_subject_id("p27"), "P27")
        self.assertEqual(normalize_subject_id("H38"), "H38")

    def test_parse_normal_circle_file(self):
        filePath = os.path.join(self.raw_dir, "HealthyMeander", "mea1-H1.jpg")
        if os.path.exists(filePath):
            rec = parse_newhandpd_file(filePath, self.raw_dir)
            self.assertIsNotNone(rec)
            self.assertEqual(rec.class_name, "Healthy")
            self.assertEqual(rec.label, 0)
            self.assertEqual(rec.drawing_type, "meander")
            self.assertEqual(rec.drawing_index, 1)
            self.assertEqual(rec.subject_id, "H01")
            self.assertEqual(rec.anomaly_flags, "none")

    def test_parse_anomaly_mea5_p8(self):
        filePath = os.path.join(self.raw_dir, "PatientMeander", "mea5-P8.jpg")
        if os.path.exists(filePath):
            rec = parse_newhandpd_file(filePath, self.raw_dir)
            self.assertIsNotNone(rec)
            self.assertEqual(rec.class_name, "Parkinson")
            self.assertEqual(rec.label, 1)
            self.assertEqual(rec.drawing_type, "meander")
            self.assertEqual(rec.drawing_index, 4)  # Mapped to 4
            self.assertEqual(rec.subject_id, "P08")
            self.assertIn("non_standard_index_mea5_mapped_to_4", rec.anomaly_flags)

    def test_parse_healthy_circle_folder_class_mismatch(self):
        filePath = os.path.join(self.raw_dir, "HealthyCircle", "circA-P1.jpg")
        if os.path.exists(filePath):
            rec = parse_newhandpd_file(filePath, self.raw_dir)
            self.assertIsNotNone(rec)
            self.assertEqual(rec.class_name, "Healthy")
            self.assertEqual(rec.label, 0)
            self.assertEqual(rec.drawing_type, "circle")
            self.assertEqual(rec.subject_id, "H01")
            self.assertIn("folder_class_mismatch", rec.anomaly_flags)


if __name__ == "__main__":
    unittest.main()
