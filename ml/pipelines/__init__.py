"""End-to-end ParkinDraw ML pipelines."""

from pipelines.evaluate import run_evaluation_pipeline
from pipelines.full_pipeline import run_full_pipeline
from pipelines.preparation import run_preparation_pipeline
from pipelines.train import run_training_pipeline

__all__ = [
    "run_evaluation_pipeline",
    "run_full_pipeline",
    "run_preparation_pipeline",
    "run_training_pipeline",
]
