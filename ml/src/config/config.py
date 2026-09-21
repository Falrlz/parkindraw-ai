"""Centralized path constants, dataset schemas, and configuration loaders for ParkinDraw."""

import re
from pathlib import Path
from typing import Any

import yaml

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Base workspace directories (ml/ root)
ML_ROOT = Path(__file__).resolve().parents[2]

# Standard data and artifact directories
DATA_DIR = ML_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
SPLITS_DIR = DATA_DIR / "splits"
MASTER_MANIFEST_PATH = SPLITS_DIR / "master_manifest.csv"

ARTIFACTS_DIR = ML_ROOT / "artifacts"
MODELS_DIR = ARTIFACTS_DIR / "models"
REPORTS_DIR = ARTIFACTS_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
TRACKING_DIR = ARTIFACTS_DIR / "tracking"

# YAML configuration paths
CONFIGS_DIR = ML_ROOT / "configs"
TRAIN_CONFIG_PATH = CONFIGS_DIR / "experiments" / "resnet18.yaml"
DEFAULT_CONFIG_PATH = TRAIN_CONFIG_PATH

# Dataset schemas, patterns, and mappings
DRAWING_TYPES: tuple[str, ...] = ("circle", "meander", "spiral")

# Mapping folder names to class name, label, and drawing type
FOLDER_SCHEMA: dict[str, tuple[str, int, str]] = {
    "HealthyCircle": ("Healthy", 0, "circle"),
    "HealthyMeander": ("Healthy", 0, "meander"),
    "HealthySpiral": ("Healthy", 0, "spiral"),
    "PatientCircle": ("Parkinson", 1, "circle"),
    "PatientMeander": ("Parkinson", 1, "meander"),
    "PatientSpiral": ("Parkinson", 1, "spiral"),
}

# Regex patterns to parse subject numbers and drawing indices from filenames
FILENAME_PATTERNS: dict[str, re.Pattern[str]] = {
    "circle": re.compile(r"circA-[HhPp](\d+)$", re.IGNORECASE),
    "meander": re.compile(r"mea(\d+)-[HhPp](\d+)$", re.IGNORECASE),
    "spiral": re.compile(r"sp(\d+)-[HhPp](\d+)$", re.IGNORECASE),
}

# Known dataset anomaly correction (subject P08 meander index 5 to 4)
DRAWING_INDEX_OVERRIDES: dict[tuple[str, str], int] = {
    ("PatientMeander", "mea5-p8"): 4,
}

# Standard drawing index bounds per subject
CIRCLE_DRAWING_INDEX: int = 1
MAX_DRAWING_INDEX: int = 4

# Default training and splitting constants
DEFAULT_SEED: int = 42
DEFAULT_HOLDOUT_SIZE: float = 0.2
DEFAULT_CV_FOLDS: int = 3
DEFAULT_BATCH_SIZE: int = 32
DEFAULT_NUM_WORKERS: int = 0

# Columns extracted during raw image scanning
BASE_MANIFEST_COLUMNS: list[str] = [
    "filepath",
    "filename",
    "class_name",
    "label",
    "drawing_type",
    "drawing_index",
    "subject_id",
]

# Standard columns included in audited manifest
MANIFEST_COLUMNS: list[str] = [
    "filepath",
    "filename",
    "class_name",
    "label",
    "drawing_type",
    "drawing_index",
    "subject_id",
    "image_hash",
    "cluster_id",
]

# Preprocessing and computer vision constants
IMAGE_SIZE: int = 224
IMAGENET_MEAN: tuple[float, float, float] = (0.485, 0.456, 0.406)
IMAGENET_STD: tuple[float, float, float] = (0.229, 0.224, 0.225)

# Data augmentation hyperparameters
MAX_ROTATION_DEGREES: float = 10.0
MAX_TRANSLATE_FRACTION: float = 0.05
SCALE_RANGE: tuple[float, float] = (0.95, 1.05)
PAPER_FILL: int = 255

# Model architecture and hardware defaults
NUM_CLASSES: int = 2
FEATURE_DIM: int = 512
DEFAULT_DEVICE: str = "auto"

# Optimization and learning rate scheduling defaults
DEFAULT_EARLY_STOPPING_PATIENCE: int = 5
DEFAULT_REDUCE_LR_PATIENCE: int = 2
DEFAULT_REDUCE_LR_FACTOR: float = 0.5
DEFAULT_MIN_LR: float = 1e-6

# MLflow experiment tracking constants
MLFLOW_TRACKING_URI: str = "sqlite:///artifacts/tracking/mlflow.db"
MLFLOW_EXPERIMENT_NAME: str = "ParkinDraw_ResNet18"


def resolve_path(
    path_like: str | Path,
    ) -> Path:

    """Resolve a path relative to ML_ROOT if it is not already absolute."""
    p = Path(path_like)
    return p if p.is_absolute() else ML_ROOT / p


def load_config(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    ) -> dict[str, Any]:

    """Load configuration dictionary from a YAML file."""
    path = resolve_path(config_path)
    if not path.is_file():
        logger.warning("Config file not found at '%s'. Returning empty dictionary.", path)
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
