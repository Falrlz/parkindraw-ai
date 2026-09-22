"""Pytest test configuration and reusable fixtures for ParkinDraw backend."""

import io
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Provide a TestClient instance wrapped in the application lifespan context."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def synthetic_png_image() -> bytes:
    """Generate in-memory valid RGB PNG image bytes."""
    buffer = io.BytesIO()
    image = Image.new("RGB", (256, 256), color=(255, 255, 255))
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def synthetic_jpeg_image() -> bytes:
    """Generate in-memory valid RGB JPEG image bytes."""
    buffer = io.BytesIO()
    image = Image.new("RGB", (256, 256), color=(240, 240, 240))
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture
def synthetic_grayscale_image() -> bytes:
    """Generate in-memory Grayscale (L) image bytes to test channel conversion."""
    buffer = io.BytesIO()
    image = Image.new("L", (200, 200), color=128)
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def corrupt_image_bytes() -> bytes:
    """Generate corrupted non-image byte sequence."""
    return b"GARBAGE_PAYLOAD_NOT_A_VALID_IMAGE_HEADER"
