"""Tests for single drawing and multi-modal screening session inference endpoints."""

import io

from fastapi.testclient import TestClient


def test_predict_single_circle(client: TestClient, synthetic_png_image: bytes) -> None:
    """Test single prediction on Circle drawing image."""
    files = {"file": ("circle_test.png", io.BytesIO(synthetic_png_image), "image/png")}
    data = {"modality": "circle"}

    response = client.post("/api/v1/predict/single", files=files, data=data)
    assert response.status_code == 200

    result = response.json()
    assert "prediction" in result
    assert "clinical_disclaimer" in result

    pred = result["prediction"]
    assert pred["modality"] == "circle"
    assert pred["prediction"] in ("Healthy", "Parkinson")
    assert pred["prediction_code"] in (0, 1)
    assert 0.0 <= pred["confidence"] <= 1.0
    assert 0.0 <= pred["probabilities"]["Healthy"] <= 1.0
    assert 0.0 <= pred["probabilities"]["Parkinson"] <= 1.0


def test_predict_single_meander(
    client: TestClient, synthetic_jpeg_image: bytes
) -> None:
    """Test single prediction on Meander drawing image with JPEG format."""
    files = {
        "file": ("meander_test.jpg", io.BytesIO(synthetic_jpeg_image), "image/jpeg")
    }
    data = {"modality": "meander"}

    response = client.post("/api/v1/predict/single", files=files, data=data)
    assert response.status_code == 200

    pred = response.json()["prediction"]
    assert pred["modality"] == "meander"
    assert pred["prediction"] in ("Healthy", "Parkinson")


def test_predict_single_spiral_grayscale(
    client: TestClient, synthetic_grayscale_image: bytes
) -> None:
    """Test single prediction with grayscale image automatically converted to RGB."""
    files = {
        "file": (
            "spiral_gray.png",
            io.BytesIO(synthetic_grayscale_image),
            "image/png",
        )
    }
    data = {"modality": "spiral"}

    response = client.post("/api/v1/predict/single", files=files, data=data)
    assert response.status_code == 200

    pred = response.json()["prediction"]
    assert pred["modality"] == "spiral"


def test_predict_session_complete(
    client: TestClient, synthetic_png_image: bytes
) -> None:
    """Test complete multi-modal screening session with all 3 drawings."""
    files = {
        "circle_file": (
            "circle.png",
            io.BytesIO(synthetic_png_image),
            "image/png",
        ),
        "meander_file": (
            "meander.png",
            io.BytesIO(synthetic_png_image),
            "image/png",
        ),
        "spiral_file": (
            "spiral.png",
            io.BytesIO(synthetic_png_image),
            "image/png",
        ),
    }

    response = client.post("/api/v1/predict/session", files=files)
    assert response.status_code == 200

    session = response.json()
    assert "session_id" in session
    assert session["fusion_prediction"] in ("Healthy", "Parkinson")
    assert session["fusion_prediction_code"] in (0, 1)
    assert 0.0 <= session["fusion_probability"] <= 1.0
    assert session["threshold"] == 0.50
    assert "circle" in session["drawings"]
    assert "meander" in session["drawings"]
    assert "spiral" in session["drawings"]
    assert "clinical_disclaimer" in session


def test_predict_session_with_custom_threshold(
    client: TestClient, synthetic_png_image: bytes
) -> None:
    """Test session prediction with an explicit custom decision threshold."""
    files = {
        "circle_file": ("c.png", io.BytesIO(synthetic_png_image), "image/png"),
        "meander_file": ("m.png", io.BytesIO(synthetic_png_image), "image/png"),
        "spiral_file": ("s.png", io.BytesIO(synthetic_png_image), "image/png"),
    }
    data = {"threshold": "0.75"}

    response = client.post("/api/v1/predict/session", files=files, data=data)
    assert response.status_code == 200
    assert response.json()["threshold"] == 0.75
