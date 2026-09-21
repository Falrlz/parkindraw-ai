from pathlib import Path

import torch
from torch import nn
from torchvision.models import ResNet18_Weights, resnet18

from src.config.config import FEATURE_DIM, NUM_CLASSES


class FrozenResNet18(nn.Module):
    """ResNet-18 backbone with frozen weights and a trainable linear classification head."""

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

        for param in self.backbone.parameters():
            param.requires_grad = False

    def train(
        self,
        mode: bool = True,
        ) -> "FrozenResNet18":

        """Set training mode for the classification head while keeping backbone in eval."""
        super().train(mode)
        self.backbone.eval()
        return self

    def forward(
        self,
        images: torch.Tensor,
        ) -> torch.Tensor:

        """Extract features with frozen backbone and compute class logits."""
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

    """Instantiate FrozenResNet18 and move it to the target device."""
    model = FrozenResNet18(num_classes=num_classes, pretrained=pretrained, dropout=dropout)
    return model.to(resolve_device(device))


def trainable_parameters(
    model: nn.Module,
    ) -> list[str]:

    """Return names of all trainable parameters requiring gradients."""
    return [name for name, p in model.named_parameters() if p.requires_grad]


def resolve_device(
    requested: str | torch.device = "auto",
    ) -> torch.device:

    """Resolve target device ('cuda' if available, otherwise 'cpu')."""
    if isinstance(requested, torch.device):
        return requested
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(requested)


def save_head(
    model: FrozenResNet18,
    path: str | Path,
    ) -> Path:

    """Save linear classification head weights to disk."""
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.head.state_dict(), target_path)
    return target_path


def load_head(
    path: str | Path,
    *,
    device: str | torch.device = "cpu",
    dropout: float = 0.0,
    pretrained: bool = True,
    ) -> FrozenResNet18:

    """Rebuild FrozenResNet18 and load trained classification head weights."""
    target_device = resolve_device(device)
    model = build_model(pretrained=pretrained, dropout=dropout, device=target_device)
    state = torch.load(path, map_location=target_device, weights_only=True)
    model.head.load_state_dict(state)
    return model
