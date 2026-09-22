"""Model metadata and evaluation benchmark information endpoints."""

from fastapi import APIRouter

from app.schemas.models_info import (
    ModalityBenchmark,
    ModalityModelInfo,
    ModelsInfoResponse,
)
from app.services.model_loader import model_registry

router = APIRouter()


@router.get(
    "/models/info",
    response_model=ModelsInfoResponse,
    summary="Get model metadata and holdout benchmark results",
    description="Returns detailed architectural metadata, parameter counts, and clinical benchmark evaluation metrics.",
)
def get_models_info() -> ModelsInfoResponse:
    """Retrieve operational specifications and clinical benchmark metrics for all models."""
    benchmarks = {
        "circle": ModalityBenchmark(
            accuracy=0.9231,
            precision=0.8571,
            recall=1.0000,
            f1_score=0.9231,
            roc_auc=0.9762,
            test_samples=13,
        ),
        "meander": ModalityBenchmark(
            accuracy=0.8846,
            precision=0.8214,
            recall=0.9583,
            f1_score=0.8846,
            roc_auc=0.9360,
            test_samples=52,
        ),
        "spiral": ModalityBenchmark(
            accuracy=0.8846,
            precision=0.8000,
            recall=1.0000,
            f1_score=0.8889,
            roc_auc=0.9911,
            test_samples=52,
        ),
    }

    models_info = {
        modality: ModalityModelInfo(
            modality=modality,
            architecture="ResNet-18 (Frozen ImageNet Backbone)",
            input_size=[3, 224, 224],
            active_parameters=1026,
            total_parameters=11177538,
            artifact_file=f"resnet18_{modality}.pt",
            is_loaded=model_registry.is_model_loaded(modality),
            benchmark_metrics=benchmarks[modality],
        )
        for modality in ["circle", "meander", "spiral"]
    }

    macro_avg = ModalityBenchmark(
        accuracy=0.8974,
        precision=0.8262,
        recall=0.9861,
        f1_score=0.8989,
        roc_auc=0.9678,
        test_samples=117,
    )

    return ModelsInfoResponse(
        models=models_info,
        dataset="NewHandPD (594 images, 66 subjects)",
        macro_average_metrics=macro_avg,
    )
