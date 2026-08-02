"""Shared fixture: a synthetic dataset mirroring the NewHandPD structure.

The real archive is not tracked in Git, so every test runs against a generated
dataset. Its value lies in reproducing the source archive's quirks rather than
in being tidy -- a clean fixture would let genuinely broken code pass:

- circle files use the `P` prefix in both class folders;
- one healthy circle uses a lowercase token;
- the eighth Parkinson subject has `mea5` instead of `mea4`;
- a pair of Parkinson subjects share byte-identical images.
"""

import hashlib

import pytest
from PIL import Image

HEALTHY_SUBJECTS = 8
PARKINSON_SUBJECTS = 8

DRAWINGS_PER_TYPE = 4
IMAGES_PER_SUBJECT = 1 + 2 * DRAWINGS_PER_TYPE  # one circle, four each otherwise

# Must be 8: the override in dataset.py is deliberately specific to `mea5-P8`,
# matching the anomaly that genuinely exists in the NewHandPD archive.
MEA5_SUBJECT = 8
# The healthy subject whose circle filename uses a lowercase token.
LOWERCASE_SUBJECT = 5
# The original archive contains distinct subjects whose meanders and spirals
# are pixel-for-pixel identical. This Parkinson subject reproduces that anomaly:
# its image content is taken from the source subject, so the bytes match.
DUPLICATE_SUBJECTS = {6: 1}


def _write_image(path, content: str, size=(8, 8)) -> None:
    """Write an image whose bytes are fully determined by `content`.

    Two calls with the same `content` produce byte-identical files, and
    different `content` produces different files. That is what makes the
    duplicate detection in splits.py genuinely testable.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(content.encode()).digest()
    image = Image.new("RGB", size)
    image.putdata(
        [
            tuple(digest[(i * 3 + channel) % len(digest)] for channel in range(3))
            for i in range(size[0] * size[1])
        ]
    )
    image.save(path)


def _build_class(root, folder, token, subjects, *, mea5=None, lowercase=None):
    for number in range(1, subjects + 1):
        # A duplicate subject borrows the image content of its source subject.
        source = DUPLICATE_SUBJECTS.get(number, number) if token == "P" else number

        circle_token = "p" if number == lowercase else "P"
        _write_image(
            root / f"{folder}Circle" / f"circA-{circle_token}{number}.jpg",
            f"{folder}-circle-{source}",
        )

        for index in range(1, DRAWINGS_PER_TYPE + 1):
            meander = 5 if (number == mea5 and index == DRAWINGS_PER_TYPE) else index
            _write_image(
                root / f"{folder}Meander" / f"mea{meander}-{token}{number}.jpg",
                f"{folder}-meander-{source}-{index}",
            )
            _write_image(
                root / f"{folder}Spiral" / f"sp{index}-{token}{number}.jpg",
                f"{folder}-spiral-{source}-{index}",
            )


@pytest.fixture
def raw_dir(tmp_path):
    """Build the complete synthetic dataset and return its root path."""
    root = tmp_path / "raw"
    _build_class(root, "Healthy", "H", HEALTHY_SUBJECTS, lowercase=LOWERCASE_SUBJECT)
    _build_class(root, "Patient", "P", PARKINSON_SUBJECTS, mea5=MEA5_SUBJECT)
    return root


@pytest.fixture
def duplicate_cluster():
    """The subjects whose images are byte-identical and must never separate."""
    return tuple(
        sorted(f"P{n:02d}" for pair in DUPLICATE_SUBJECTS.items() for n in pair)
    )


@pytest.fixture
def total_subjects():
    return HEALTHY_SUBJECTS + PARKINSON_SUBJECTS


@pytest.fixture
def total_images(total_subjects):
    return total_subjects * IMAGES_PER_SUBJECT


@pytest.fixture
def mea5_subject():
    return MEA5_SUBJECT


@pytest.fixture
def lowercase_subject():
    return LOWERCASE_SUBJECT
