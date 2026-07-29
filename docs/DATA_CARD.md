# Data Card --- NewHandPD Dataset

## 📌 Dataset Overview

* **Dataset Name**: NewHandPD
* **Domain**: Computer Vision for AI-assisted Parkinson's Disease Screening
* **Modalities**: Static / Offline Handwriting & Drawing Images
* **Drawings Analyzed**: Circle, Meander, Spiral
* **Total Subjects**: 66 subjects (35 Healthy, 31 Parkinson)
* **Total Images**: 594 images (9 drawings per subject)
* **Raw Data Location**: `data/raw/newhandpd/` (git-ignored)

---

## 🏷️ Class & Subject Distribution

| Class Name | Label | Subject Count | Subjects IDs | Drawings per Subject | Total Images |
|---|---|---|---|---|---|
| Healthy | `0` | 35 | `H01` -- `H38` (non-sequential) | 1 Circle, 4 Meander, 4 Spiral | 315 |
| Parkinson | `1` | 31 | `P01` -- `P32` (non-sequential) | 1 Circle, 4 Meander, 4 Spiral | 279 |
| **Total** | -- | **66** | -- | **9 drawings per subject** | **594** |

---

## 🔍 Anomaly Handling Policy

1. **Folder-Class Primacy**:
   - Folders `HealthyCircle`, `HealthyMeander`, `HealthySpiral` are assigned Label `0` (Healthy).
   - Folders `PatientCircle`, `PatientMeander`, `PatientSpiral` are assigned Label `1` (Parkinson).
   - Inconsistencies like `circA-P1.jpg` inside `HealthyCircle` are assigned Label `0` (Healthy) with subject ID `H01` and flagged in metadata as `folder_class_mismatch_p_token_in_healthy_folder`.

2. **File Anomaly `mea5-P8.jpg`**:
   - In `PatientMeander`, subject `P08` contains files `mea1-P8.jpg`, `mea2-P8.jpg`, `mea3-P8.jpg`, and `mea5-P8.jpg`.
   - `mea5-P8.jpg` represents the 4th meander drawing attempt of subject `P08`.
   - Parser maps `drawing_index = 4` for `mea5-P8.jpg` and records `anomaly_flags = "non_standard_index_mea5_mapped_to_4"`.

3. **Case Sensitivity**:
   - Filenames with lowercase tokens (e.g. `circA-p27.jpg`) are normalized to uppercase `P27` and flagged as `lowercase_subject_token`.

---

## 🔒 Exact Duplicate Handling & Data Leakage Prevention

* **Checksum Algorithm**: SHA-256
* **Exact Duplicate Groups Detected**: 36 groups (comprising 80 images)
* **Distribution**: Exact duplicate images exist across Parkinson subjects in `PatientMeander` and `PatientSpiral`.
* **Policy**: All exact duplicate images identified in `data/metadata/duplicate_groups.csv` MUST be grouped together with their associated subjects during data splitting.
* **Leakage Gate**:
  $$\text{subject(train)} \cap \text{subject(test)} = \emptyset$$
  $$\text{duplicate\_group(train)} \cap \text{duplicate\_group(test)} = \emptyset$$

---

## 📄 Licensing & Data Governance

* **Raw Data Immutability**: The raw dataset files in `data/raw/newhandpd/` are strictly read-only and immutable. No resizing, renaming, or modifying is applied directly to raw files.
* **Version Control**: Raw dataset image files and PDF literature are excluded from Git repository via `.gitignore`.
* **Reproducible Manifests**: Metadata manifests (`images.csv`, `subjects.csv`, `duplicate_groups.csv`, `audit_report.json`) are checked into Git for 100% experiment reproducibility.
