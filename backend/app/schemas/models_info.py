"""Model metadata and benchmark specification schemas."""

from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field


class ModalityBenchmark(BaseModel):
    """Clinical performance metrics on locked holdout evaluation set."""

    accuracy: float = Field(..., description="Classification accuracy")
    precision: float = Field(..., description="Positive predictive value")
    recall: float = Field(..., description="Screening sensitivity")
    f1_score: float = Field(..., description="Harmonic mean of precision and recall")
    roc_auc: float = Field(..., description="Area under the ROC curve")
    test_samples: int = Field(..., description="Holdout sample support size")


class ModalityModelInfo(BaseModel):
    """Architectural and operational metadata for a drawing modality."""

    modality: str = Field(..., description="Drawing modality name")
    architecture: str = Field(default="ResNet-18 (Frozen ImageNet Backbone)")
    input_size: List[int] = Field(default=[3, 224, 224])
    active_parameters: int = Field(default=1026)
    total_parameters: int = Field(default=11177538)
    artifact_file: str = Field(..., description="Canonical model checkpoint filename")
    is_loaded: bool = Field(..., description="Memory load readiness status")
    benchmark_metrics: ModalityBenchmark = Field(
        ..., description="Clinical holdout benchmark metrics"
    )


class ModelsInfoResponse(BaseModel):
    """Aggregate models information response payload."""

    models: Dict[str, ModalityModelInfo] = Field(
        ..., description="Metadata keyed by modality"
    )
    dataset: str = Field(default="NewHandPD (594 images, 66 subjects)")
    macro_average_metrics: ModalityBenchmark = Field(
        ..., description="Macro average metrics across all modalities"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "dataset": "NewHandPD (594 images, 66 subjects)",
                "models": {
                    "circle": {
                        "modality": "circle",
                        "architecture": "ResNet-18 (Frozen ImageNet Backbone)",
                        "input_size": [3, 224, 224],
                        "active_parameters": 1026,
                        "total_parameters": 11177538,
                        "artifact_file": "resnet18_circle.pt",
                        "is_loaded": True,
                        "benchmark_metrics": {
                            "accuracy": 0.9231,
                            "precision": 0.8571,
                            "recall": 1.0000,
                            "f1_score": 0.9231,
                            "roc_auc": 0.9762,
                            "test_samples": 13,
                        },
                    }
                },
                "macro_average_metrics": {
                    "accuracy": 0.8974,
                    "precision": 0.8262,
                    "recall": 0.9861,
                    "f1_score": 0.8989,
                    "roc_auc": 0.9678,
                    "test_samples": 117,
                },
            }
        }
    )
