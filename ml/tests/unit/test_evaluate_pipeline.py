"""Tests for the evaluate pipeline orchestrator."""

from pipelines import evaluate as eval_pipeline


def test_evaluate_pipeline_orchestration(monkeypatch):
    calls = []

    def mock_load_config(path):
        return {"splits_dir": "test_splits"}

    def mock_load_manifest(path):
        return None

    def mock_filter_holdout(df):
        return None

    def mock_evaluate_models(df, cfg, drawing_types):
        calls.append(("eval_models", drawing_types))
        return {"circle": {"metrics": {}}}

    def mock_generate_reports(results, cfg):
        calls.append(("gen_reports", results))

    monkeypatch.setattr(eval_pipeline, "load_config", mock_load_config)
    monkeypatch.setattr(eval_pipeline, "load_manifest", mock_load_manifest)
    monkeypatch.setattr(eval_pipeline, "filter_holdout", mock_filter_holdout)
    monkeypatch.setattr(eval_pipeline, "evaluate_holdout_models", mock_evaluate_models)
    monkeypatch.setattr(eval_pipeline, "generate_evaluation_reports", mock_generate_reports)

    results = eval_pipeline.run_evaluation_pipeline(
        config_path="test_config.yaml",
        drawing_types=["circle"],
    )

    assert len(calls) == 2
    assert calls[0][0] == "eval_models"
    assert calls[1][0] == "gen_reports"
    assert "circle" in results
