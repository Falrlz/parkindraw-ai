"""Tests for the master full_pipeline orchestrator."""

from pipelines import full_pipeline as fp


def test_full_pipeline_orchestration(monkeypatch):
    calls = []

    def mock_prep(**kwargs):
        calls.append(("prep", kwargs))

    def mock_train(**kwargs):
        calls.append(("train", kwargs))
        return {"circle": {"metrics": {"accuracy": 0.9}}}

    def mock_eval(**kwargs):
        calls.append(("eval", kwargs))
        return {"circle": {"metrics": {"accuracy": 0.85}}}

    monkeypatch.setattr(fp, "run_preparation_pipeline", mock_prep)
    monkeypatch.setattr(fp, "run_training_pipeline", mock_train)
    monkeypatch.setattr(fp, "run_evaluation_pipeline", mock_eval)

    result = fp.run_full_pipeline(
        train_config_path="configs/test_train.yaml",
        drawing_types=["circle"],
    )

    assert len(calls) == 3
    assert calls[0][0] == "prep"
    assert calls[1][0] == "train"
    assert calls[2][0] == "eval"
    assert "training" in result
    assert "evaluation" in result
