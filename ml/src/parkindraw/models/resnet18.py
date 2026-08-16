"""Frozen ImageNet-pretrained ResNet-18 with a trainable two-class head.

Locked by `0_LITERATURE_REVIEW.md` section 5: with 53 development subjects,
fine-tuning the whole backbone would overfit immediately. Only the final
classification layer is trained.

Freezing has two halves, and missing the second is a common mistake:

1. set `requires_grad = False` on every backbone parameter;
2. keep the BatchNorm layers in eval mode. Parameters alone are not enough --
   in train mode BatchNorm keeps updating its running mean and variance, so the
   backbone would still drift between epochs and runs would stop being
   reproducible.
"""

import torch
from torch import nn
from torchvision.models import ResNet18_Weights, resnet18

NUM_CLASSES = 2
FEATURE_DIM = 512


class FrozenResNet18(nn.Module):
    """ResNet-18 whose backbone never changes.

    `train()` is overridden so the backbone stays in eval mode even when the
    module is switched to training. Only the head follows the requested mode.
    """

    def __init__(
        self,
        num_classes: int = NUM_CLASSES,
        pretrained: bool = True,
        dropout: float = 0.0,
    ) -> None:
        super().__init__()
        weights = ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        backbone = resnet18(weights=weights)

        backbone.fc = nn.Identity()
        self.backbone = backbone
        self.dropout = nn.Dropout(dropout)
        self.head = nn.Linear(FEATURE_DIM, num_classes)

        for parameter in self.backbone.parameters():
            parameter.requires_grad = False

    def train(self, mode: bool = True) -> "FrozenResNet18":
        """Put the head in the requested mode, but pin the backbone to eval."""
        super().train(mode)
        self.backbone.eval()
        return self

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        # No gradients are needed through the backbone, which also keeps the
        # backward pass cheap enough to train comfortably on CPU.
        with torch.no_grad():
            features = self.backbone(images)
        return self.head(self.dropout(features))


def build_model(
    num_classes: int = NUM_CLASSES,
    *,
    pretrained: bool = True,
    dropout: float = 0.0,
    device: str | torch.device = "cpu",
) -> FrozenResNet18:
    """Build the model and move it to `device`.

    `device` is always explicit so the same code runs unchanged on CPU and GPU.
    """
    model = FrozenResNet18(
        num_classes=num_classes,
        pretrained=pretrained,
        dropout=dropout,
    )
    return model.to(device)


def trainable_parameters(model: nn.Module) -> list[str]:
    """Names of the parameters that will actually receive gradients."""
    return [name for name, p in model.named_parameters() if p.requires_grad]


def resolve_device(requested: str = "auto") -> torch.device:
    """Turn a config value into a concrete device.

    Keeping this in one place is what makes renting a GPU a config change
    rather than a code change.
    """
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(requested)
