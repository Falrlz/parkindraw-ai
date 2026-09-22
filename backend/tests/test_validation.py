"""Validation and defensive error handling tests."""

import io

from fastapi.testclient import TestClient


def test_predict_invalid_modality(
    client: TestClient, synthetic_png_image: bytes
) -> None:
    """Ensure invalid modality returns HTTP 422 Unprocessable Entity."""
    files = {"file": ("test.png", io.BytesIO(synthetic_png_image), "image/png")}
    data = {"modality": "unsupported_drawing"}

    response = client.post("/api/v1/predict/single", files=files, data=data)
    assert response.status_code == 422


def test_predict_corrupt_image(client: TestClient, corrupt_image_bytes: bytes) -> None:
    """Ensure non-image bitstream returns HTTP 400 Bad Request."""
    files = {"file": ("corrupt.png", io.BytesIO(corrupt_image_bytes), "image/png")}
    data = {"modality": "spiral"}

    response = client.post("/api/v1/predict/single", files=files, data=data)
    assert response.status_code == 400
    assert "could not be decoded as a valid image" in response.json()["detail"]


def test_predict_empty_image(client: TestClient) -> None:
    """Ensure 0-byte file returns HTTP 400 Bad Request."""
    files = {"file": ("empty.png", io.BytesIO(b""), "image/png")}
    data = {"modality": "spiral"}

    response = client.post("/api/v1/predict/single", files=files, data=data)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]


def test_predict_disallowed_extension(
    client: TestClient, synthetic_png_image: bytes
) -> None:
    """Ensure unsupported file extension is rejected with HTTP 400."""
    files = {
        "file": (
            "drawing.pdf",
            io.BytesIO(synthetic_png_image),
            "application/pdf",
        )
    }
    data = {"modality": "circle"}

    response = client.post("/api/v1/predict/single", files=files, data=data)
    assert response.status_code == 400
    assert "File extension '.pdf' is not permitted" in response.json()["detail"]


def test_predict_session_missing_modality(
    client: TestClient, synthetic_png_image: bytes
) -> None:
    """Ensure session endpoint requires all 3 drawing files."""
    # Omit spiral_file
    files = {
        "circle_file": ("c.png", io.BytesIO(synthetic_png_image), "image/png"),
        "meander_file": ("m.png", io.BytesIO(synthetic_png_image), "image/png"),
    }

    response = client.post("/api/v1/predict/session", files=files)
    assert response.status_code == 422
