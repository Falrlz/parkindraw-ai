"""Model architecture definitions and singleton ModelRegistry service.

Implements standalone ResNet-18 model architecture and lifecycle management
without external dependencies on the training pipeline package.
"""

from pathlib import Path
from typing import Dict, Optional

import torch
import torch.nn as nn
from torchvision.models import resnet18

from app.core.logging import get_logger

logger = get_logger("model_loader")


class FrozenResNet18(nn.Module):
    """ResNet-18 deep transfer learning classifier.

    Contains a frozen convolutional feature extraction backbone and a custom
    trainable linear classification head matching the trained ML artifacts.
    """

    def __init__(self, num_classes: int = 2, dropout_rate: float = 0.0) -> None:
        """Initialize FrozenResNet18 architecture.

        Args:
            num_classes: Number of categorical output logits (default: 2).
            dropout_rate: Dropout probability in the classification head (default: 0.0).
        """
        super().__init__()
        backbone = resnet18(weights=None)
        backbone.fc = nn.Identity()

        self.backbone = backbone
        self.dropout = nn.Dropout(p=dropout_rate)
        self.head = nn.Linear(in_features=512, out_features=num_classes)

        for param in self.backbone.parameters():
            param.requires_grad = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Compute forward inference pass.

        Args:
            x: Input batch tensor of shape [B, 3, 224, 224].

        Returns:
            torch.Tensor: Unnormalized class logits of shape [B, 2].
        """
        with torch.no_grad():
            features = self.backbone(x)
        logits = self.head(self.dropout(features))
        return logits


class ModelRegistry:
    """Singleton registry managing in-memory PyTorch models for inference."""

    _instance: Optional["ModelRegistry"] = None

    def __new__(cls) -> "ModelRegistry":
        """Enforce singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize empty model registry."""
        if getattr(self, "_initialized", False):
            return

        self._models: Dict[str, FrozenResNet18] = {}
        self._device: torch.device = torch.device("cpu")
        self._initialized = True

    @property
    def device(self) -> torch.device:
        """Return the active compute device for model inference."""
        return self._device

    def resolve_device(self, preferred_device: str = "auto") -> torch.device:
        """Determine and configure the optimal compute device.

        Args:
            preferred_device: One of 'auto', 'cuda', or 'cpu'.

        Returns:
            torch.device: Resolved PyTorch device.
        """
        if preferred_device == "cuda" and torch.cuda.is_available():
            self._device = torch.device("cuda")
        elif preferred_device == "auto" and torch.cuda.is_available():
            self._device = torch.device("cuda")
        else:
            self._device = torch.device("cpu")

        logger.info(f"Resolved inference compute device: {self._device}")
        return self._device

    def load_all_models(
        self, models_dir: Path, preferred_device: str = "auto"
    ) -> Dict[str, bool]:
        """Load canonical model checkpoints for all three modalities into memory.

        Args:
            models_dir: Directory containing resnet18_{modality}.pt checkpoints.
            preferred_device: Hardware acceleration preference ('auto', 'cuda', 'cpu').

        Returns:
            Dict[str, bool]: Loading outcome status per modality.
        """
        self.resolve_device(preferred_device)
        modalities = ["circle", "meander", "spiral"]
        results: Dict[str, bool] = {}

        logger.info(f"Loading canonical models from: {models_dir.resolve()}")

        for modality in modalities:
            checkpoint_path = models_dir / f"resnet18_{modality}.pt"
            success = self.load_model(modality=modality, checkpoint_path=checkpoint_path)
            results[modality] = success

        loaded_count = sum(results.values())
        logger.info(
            f"Model registry initialization complete: {loaded_count}/{len(modalities)} "
            f"models successfully loaded into memory."
        )
        return results

    def load_model(self, modality: str, checkpoint_path: Path) -> bool:
        """Load an individual modality model checkpoint into memory.

        Args:
            modality: Drawing modality name ('circle', 'meander', 'spiral').
            checkpoint_path: Path to the .pt checkpoint file.

        Returns:
            bool: True if loaded successfully, False otherwise.
        """
        if not checkpoint_path.is_file():
            logger.warning(
                f"Checkpoint not found for modality '{modality}' at: {checkpoint_path}"
            )
            return False

        try:
            model = FrozenResNet18(num_classes=2, dropout_rate=0.0)
            checkpoint = torch.load(
                checkpoint_path,
                map_location=self._device,
                weights_only=True,
            )

            # Support both direct state_dict and wrapped state_dict
            if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
                state_dict = checkpoint["state_dict"]
            elif isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                state_dict = checkpoint["model_state_dict"]
            elif isinstance(checkpoint, dict):
                state_dict = checkpoint
            else:
                raise ValueError(
                    f"Unrecognized checkpoint format for {modality}: {type(checkpoint)}"
                )

            model.load_state_dict(state_dict)
            model.to(self._device)
            model.eval()

            self._models[modality] = model
            logger.info(f"Successfully loaded '{modality}' model checkpoint into memory.")
            return True
        except Exception as err:
            logger.error(
                f"Failed to load checkpoint for '{modality}' from {checkpoint_path}: {err}",
                exc_info=True,
            )
            return False

    def get_model(self, modality: str) -> Optional[FrozenResNet18]:
        """Retrieve the in-memory model for a specified modality.

        Args:
            modality: Drawing modality name ('circle', 'meander', 'spiral').

        Returns:
            Optional[FrozenResNet18]: Model instance or None if not loaded.
        """
        return self._models.get(modality.lower())

    def is_model_loaded(self, modality: str) -> bool:
        """Check if a specific modality model is currently ready in memory.

        Args:
            modality: Drawing modality name ('circle', 'meander', 'spiral').

        Returns:
            bool: True if loaded, False otherwise.
        """
        return modality.lower() in self._models

    def get_status(self) -> Dict[str, bool]:
        """Return readiness status dictionary for all three modalities.

        Returns:
            Dict[str, bool]: Modality readiness mapping.
        """
        return {
            "circle": self.is_model_loaded("circle"),
            "meander": self.is_model_loaded("meander"),
            "spiral": self.is_model_loaded("spiral"),
        }


# Global singleton instance
model_registry = ModelRegistry()
