"""Locked holdout evaluation service and report generator."""

from pathlib import Path
from typing import Any

import pandas as pd
import torch
from torch import nn

from src.config.config import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_DEVICE,
    DEFAULT_NUM_WORKERS,
    DRAWING_TYPES,
    FIGURES_DIR,
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_TRACKING_URI,
    MODELS_DIR,
    RAW_DATA_DIR,
)
from src.data.manifest import filter_drawing
from src.evaluation.metrics import compute_metrics, format_metrics
from src.evaluation.plots import (
    plot_confusion_matrix,
    plot_loss_accuracy,
    plot_multi_confusion_matrices,
)
from src.models.resnet18 import load_head, resolve_device
from src.preprocessing.data_loader import create_eval_loader
from src.tracking.mlflow_tracker import setup_mlflow
from src.utils.logger import get_logger

logger = get_logger(__name__)

ALL_DRAWING_TYPES: tuple[str, ...] = DRAWING_TYPES


def evaluate_single_holdout(
    drawing_type: str,
    holdout_df: pd.DataFrame,
    cfg: dict[str, Any],
    device: torch.device,
    ) -> dict[str, Any]:

    """Evaluate a single drawing modality on locked holdout test data."""
    drawing_subset = filter_drawing(holdout_df, drawing_type)
    raw_dir = Path(cfg.get("raw_dir", RAW_DATA_DIR))
    checkpoint_dir = Path(cfg.get("checkpoint_dir", MODELS_DIR))
    model_path = checkpoint_dir / f"resnet18_{drawing_type}.pt"

    if not model_path.is_file():
        raise FileNotFoundError(f"Model checkpoint not found at: {model_path}")

    batch_size = int(cfg.get("batch_size", DEFAULT_BATCH_SIZE))
    num_workers = int(cfg.get("num_workers", DEFAULT_NUM_WORKERS))
    loader = create_eval_loader(
        drawing_subset,
        raw_dir=raw_dir,
        batch_size=batch_size,
        num_workers=num_workers,
    )

    model = load_head(model_path, device=device)
    model.eval()

    criterion = nn.CrossEntropyLoss()
    total_loss, total_samples = 0.0, 0
    all_targets, all_preds, all_probs = [], [], []

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            logits = model(images)
            loss = criterion(logits, labels)

            batch_size_curr = images.size(0)
            total_loss += loss.item() * batch_size_curr
            total_samples += batch_size_curr

            probs = torch.softmax(logits, dim=1)
            all_targets.extend(labels.cpu().tolist())
            all_preds.extend(torch.argmax(probs, dim=1).cpu().tolist())
            all_probs.extend(probs[:, 1].cpu().tolist())

    avg_loss = total_loss / max(total_samples, 1)
    metrics = compute_metrics(all_targets, all_preds, all_probs)
    metrics["holdout_loss"] = float(avg_loss)

    return {
        "drawing_type": drawing_type,
        "samples": len(drawing_subset),
        "metrics": metrics,
        "model_path": str(model_path),
        "y_true": all_targets,
        "y_pred": all_preds,
    }


def generate_training_curves(
    cfg: dict[str, Any],
    drawing_types: tuple[str, ...] | list[str] = DRAWING_TYPES,
    output_dir: str | Path = FIGURES_DIR,
    ) -> list[Path]:

    """Plot learning curves per modality from MLflow history."""
    import mlflow

    tracking_uri = cfg.get("tracking_uri", MLFLOW_TRACKING_URI)
    mlflow.set_tracking_uri(tracking_uri)
    client = mlflow.tracking.MlflowClient()
    experiment_name = cfg.get("experiment_name", MLFLOW_EXPERIMENT_NAME)
    exp = client.get_experiment_by_name(experiment_name)
    if not exp:
        return []

    runs = client.search_runs(experiment_ids=[exp.experiment_id])
    saved_plots: list[Path] = []
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for r in runs:
        dt = r.data.tags.get("drawing_type")
        if not dt or dt not in drawing_types:
            continue

        train_loss_hist = sorted(
            client.get_metric_history(r.info.run_id, "epoch_train_loss"),
            key=lambda x: x.step,
        )
        val_loss_hist = sorted(
            client.get_metric_history(r.info.run_id, "epoch_val_loss"),
            key=lambda x: x.step,
        )
        val_acc_hist = sorted(
            client.get_metric_history(r.info.run_id, "epoch_val_accuracy"),
            key=lambda x: x.step,
        )

        if not train_loss_hist:
            continue

        epochs = [m.step for m in train_loss_hist]
        t_loss = [m.value for m in train_loss_hist]
        v_loss = [m.value for m in val_loss_hist]
        v_acc = [m.value for m in val_acc_hist]

        plot_path = out_dir / f"loss_acc_{dt}.png"
        plot_loss_accuracy(
            epochs=epochs,
            train_loss=t_loss,
            val_loss=v_loss,
            val_accuracy=v_acc,
            title=f"Learning Curves - ResNet18 ({dt.capitalize()})",
            save_path=plot_path,
        )
        saved_plots.append(plot_path)

    return saved_plots


def evaluate_holdout_models(
    holdout_df: pd.DataFrame,
    cfg: dict[str, Any],
    drawing_types: list[str] | tuple[str, ...] | None = None,
    ) -> dict[str, dict[str, Any]]:

    """Evaluate trained models on the locked holdout test partition."""
    setup_mlflow(
        tracking_uri=cfg.get("tracking_uri", MLFLOW_TRACKING_URI),
        experiment_name=cfg.get("experiment_name", MLFLOW_EXPERIMENT_NAME),
    )

    device = resolve_device(cfg.get("device", DEFAULT_DEVICE))
    target_drawings = drawing_types or cfg.get("drawing_types", DRAWING_TYPES)

    logger.info("Evaluating %d locked holdout samples across %d modalities...", len(holdout_df), len(target_drawings))

    results: dict[str, dict[str, Any]] = {}
    for dt in target_drawings:
        res = evaluate_single_holdout(dt, holdout_df, cfg, device)
        results[dt] = res
        logger.info("Holdout [%s] -> %s", dt.upper(), format_metrics(res["metrics"]))

    return results


def generate_evaluation_reports(
    results: dict[str, dict[str, Any]],
    cfg: dict[str, Any],
    ) -> dict[str, Any]:

    """Generate confusion matrices, learning curves, and format terminal summary."""
    figures_dir = Path(cfg.get("figures_dir", FIGURES_DIR))
    figures_dir.mkdir(parents=True, exist_ok=True)

    cm_paths: dict[str, Path] = {}
    for dt, res in results.items():
        cm_path = figures_dir / f"confusion_matrix_{dt}.png"
        plot_confusion_matrix(
            res["y_true"],
            res["y_pred"],
            title=f"Holdout CM - {dt.capitalize()}",
            save_path=cm_path,
        )
        cm_paths[dt] = cm_path

    multi_cm_path = figures_dir / "confusion_matrix_all.png"
    plot_multi_confusion_matrices(
        {dt: (res["y_true"], res["y_pred"]) for dt, res in results.items()},
        save_path=multi_cm_path,
    )

    loss_acc_plots = generate_training_curves(cfg, list(results.keys()), output_dir=figures_dir)

    print("\n" + "=" * 80)
    print("           LOCKED HOLDOUT EVALUATION SUMMARY (TEST SET 20%)")
    print("=" * 80)
    print(f"{'Drawing':<12} {'Samples':<10} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'ROC-AUC':<10}")
    print("-" * 80)
    for dt, res in results.items():
        m = res["metrics"]
        print(
            f"{dt.capitalize():<12} "
            f"{res['samples']:<10} "
            f"{m['accuracy']:<12.4f} "
            f"{m['precision']:<12.4f} "
            f"{m['recall']:<12.4f} "
            f"{m['f1_score']:<12.4f} "
            f"{m['roc_auc']:<10.4f}"
        )
    print("=" * 80)
    print(f"\nFigures saved in '{figures_dir}':")
    print(f" - Multi Confusion Matrix: {multi_cm_path}")
    for dt, p in cm_paths.items():
        print(f" - Confusion Matrix [{dt.capitalize()}]: {p}")
    for lp in loss_acc_plots:
        print(f" - Learning Curves: {lp}")
    print()

    return {
        "multi_cm": multi_cm_path,
        "single_cms": cm_paths,
        "curves": loss_acc_plots,
    }
