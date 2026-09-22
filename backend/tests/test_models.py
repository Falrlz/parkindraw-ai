"""Tests for model metadata and holdout benchmark information endpoint."""

from fastapi.testclient import TestClient


def test_get_models_info(client: TestClient) -> None:
    """Ensure /api/v1/models/info delivers verified benchmark figures."""
    response = client.get("/api/v1/models/info")
    assert response.status_code == 200
    data = response.json()

    assert "models" in data
    assert "macro_average_metrics" in data
    assert "dataset" in data

    models = data["models"]
    for modality in ("circle", "meander", "spiral"):
        assert modality in models
        info = models[modality]
        assert info["architecture"] == "ResNet-18 (Frozen ImageNet Backbone)"
        assert info["active_parameters"] == 1026
        assert "benchmark_metrics" in info

        metrics = info["benchmark_metrics"]
        assert 0.0 <= metrics["accuracy"] <= 1.0
        assert 0.0 <= metrics["precision"] <= 1.0
        assert 0.0 <= metrics["recall"] <= 1.0
        assert 0.0 <= metrics["roc_auc"] <= 1.0

    macro = data["macro_average_metrics"]
    assert macro["test_samples"] == 117
    assert macro["accuracy"] == 0.8974
