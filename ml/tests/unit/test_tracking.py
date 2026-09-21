from pathlib import Path

import mlflow
import pytest

from src.models.resnet18 import build_model
from src.tracking.mlflow_tracker import log_training_run, setup_mlflow


def test_setup_mlflow_and_logging(tmp_path: Path):
    tracking_uri = f"sqlite:///{tmp_path / 'test_mlflow.db'}"
    setup_mlflow(tracking_uri=tracking_uri, experiment_name="Test_Exp")

    model = build_model(pretrained=False, device="cpu")
    params = {"epochs": 2, "batch_size": 4, "learning_rate": 0.001}
    metrics = {"accuracy": 0.85, "recall": 0.90, "f1_score": 0.847, "roc_auc": 0.88}

    checkpoint_dir = tmp_path / "checkpoints"
    saved_path = log_training_run(
        run_name="Test_Circle",
        drawing_type="circle",
        model=model,
        params=params,
        metrics=metrics,
        duration=1.2,
        checkpoint_dir=checkpoint_dir,
    )

    assert saved_path.is_file()
    assert saved_path.name == "resnet18_circle.pt"

    exp = mlflow.get_experiment_by_name("Test_Exp")
    assert exp is not None
    runs = mlflow.search_runs(experiment_ids=[exp.experiment_id])
    assert len(runs) >= 1
    assert runs.iloc[0]["metrics.accuracy"] == pytest.approx(0.85)
