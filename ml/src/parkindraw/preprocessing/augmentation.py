"""Conservative augmentation, applied to training data only.

With 53 development subjects -- and only 53 circle images in total -- the main
risk is overfitting. Augmentation is one of the few defences available besides
the frozen backbone, so it is enabled from the start rather than deferred.

Two transformations are deliberately excluded:

- **horizontal flip**, because a spiral has a meaningful winding direction and
  mirroring it changes the movement it represents;
- **aggressive colour jitter**, because colour is what separates the printed
  black template from the participant's blue trace.

What remains mimics how the same drawing would look if the sheet were placed
slightly differently under the camera: small rotation, small shift, small
scale.
"""

from torchvision.transforms import v2

from parkindraw.preprocessing.transforms import build_transform

MAX_ROTATION_DEGREES = 10.0
MAX_TRANSLATE_FRACTION = 0.05
SCALE_RANGE = (0.95, 1.05)

# Paper is white, so the corners exposed by a rotation must be filled white
# too. The default fill is black, which the network would read as heavy stroke
# along the edges.
PAPER_FILL = 255


def build_augmentation() -> v2.RandomAffine:
    """The geometric jitter on its own, without any preprocessing around it."""
    return v2.RandomAffine(
        degrees=MAX_ROTATION_DEGREES,
        translate=(MAX_TRANSLATE_FRACTION, MAX_TRANSLATE_FRACTION),
        scale=SCALE_RANGE,
        interpolation=v2.InterpolationMode.BILINEAR,
        fill=PAPER_FILL,
    )


def build_train_transform() -> v2.Compose:
    """Return the training pipeline: the fixed preprocessing, plus jitter.

    Built by handing the augmentation to `build_transform`, so the resize,
    tensor conversion, and normalisation can only ever come from one place.
    Evaluation and inference keep calling `build_transform` directly.
    """
    return build_transform(extra=[build_augmentation()])
