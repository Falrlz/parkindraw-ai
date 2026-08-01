"""Fixture bersama: dataset sintetis yang meniru struktur NewHandPD.

Raw dataset asli tidak masuk Git, sehingga seluruh test memakai dataset
buatan dengan keanehan penamaan yang sama seperti arsip sumber:

- file Circle memakai prefix `P` di kedua folder class;
- satu Circle Healthy memakai huruf kecil;
- subjek Parkinson ke-8 memiliki `mea5` alih-alih `mea4`.
"""

import pytest
from PIL import Image

HEALTHY_SUBJECTS = 8
PARKINSON_SUBJECTS = 8

# Harus 8: override pada dataset.py sengaja spesifik untuk `mea5-P8`,
# sesuai anomali yang benar-benar ada di arsip NewHandPD.
MEA5_SUBJECT = 8
# Subjek Healthy yang nama Circle-nya memakai huruf kecil.
LOWERCASE_SUBJECT = 5


def _write_image(path, size=(8, 8)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=(255, 255, 255)).save(path)


def _build_class(root, folder, token, subjects, *, mea5=None, lowercase=None):
    for number in range(1, subjects + 1):
        circle_token = "p" if number == lowercase else "P"
        _write_image(root / f"{folder}Circle" / f"circA-{circle_token}{number}.jpg")

        for index in range(1, 5):
            meander = 5 if (number == mea5 and index == 4) else index
            _write_image(
                root / f"{folder}Meander" / f"mea{meander}-{token}{number}.jpg"
            )
            _write_image(root / f"{folder}Spiral" / f"sp{index}-{token}{number}.jpg")


@pytest.fixture
def raw_dir(tmp_path):
    """Bangun dataset sintetis lengkap dan kembalikan path root-nya."""
    root = tmp_path / "raw"
    _build_class(root, "Healthy", "H", HEALTHY_SUBJECTS, lowercase=LOWERCASE_SUBJECT)
    _build_class(root, "Patient", "P", PARKINSON_SUBJECTS, mea5=MEA5_SUBJECT)
    return root


@pytest.fixture
def total_subjects():
    return HEALTHY_SUBJECTS + PARKINSON_SUBJECTS


@pytest.fixture
def total_images(total_subjects):
    return total_subjects * 9


@pytest.fixture
def mea5_subject():
    return MEA5_SUBJECT


@pytest.fixture
def lowercase_subject():
    return LOWERCASE_SUBJECT
