"""Training orchestration service for multi-drawing ResNet-18 models."""

import shutil
import statistics
from pathlib import Path
from typing import Any

import pandas as pd
import torch
from torch import nn

from src.config.config import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_CV_FOLDS,
    DEFAULT_DEVICE,
    DEFAULT_EARLY_STOPPING_PATIENCE,
    DEFAULT_MIN_LR,
    DEFAULT_NUM_WORKERS,
    DEFAULT_REDUCE_LR_FACTOR,
    DEFAULT_REDUCE_LR_PATIENCE,
    DEFAULT_SEED,
    DRAWING_TYPES,
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_TRACKING_URI,
    MODELS_DIR,
    NUM_CLASSES,
    RAW_DATA_DIR,
)
from src.data.manifest import filter_drawing
from src.data.splits import get_cv_folds
from src.evaluation.metrics import compute_metrics, format_metrics
from src.models.resnet18 import build_model, resolve_device
from src.preprocessing.data_loader import create_train_val_loaders
from src.tracking.mlflow_tracker import log_training_run, setup_mlflow
from src.training.engine import train_model, validate_epoch
from src.utils.logger import get_logger

logger = get_logger(__name__)

ALL_DRAWING_TYPES: tuple[str, ...] = DRAWING_TYPES


def train_single_drawing(
    drawing_type: str,
    master_manifest: pd.DataFrame,
    cfg: dict[str, Any],
    *,
    device: torch.device,
    fold: int = 0,
    checkpoint_dir: str | Path = MODELS_DIR,
    model_filename: str | None = None,
    ) -> dict[str, Any]:

    """Train, validate, and checkpoint a ResNet-18 model for one drawing modality."""
    logger.info("--- Training Modality: %s (Fold %d) ---", drawing_type.upper(), fold)

    # 1. Isolate modality subset and split with 3-fold CV
    drawing_df = filter_drawing(master_manifest, drawing_type)
    raw_dir = Path(cfg.get("raw_dir", RAW_DATA_DIR))
    seed = int(cfg.get("seed", DEFAULT_SEED))
    folds = get_cv_folds(drawing_df, n_splits=DEFAULT_CV_FOLDS, seed=seed)
    train_df, val_df = folds[fold]

    # 2. Build data loaders via data_loader factory
    batch_size = int(cfg.get("batch_size", DEFAULT_BATCH_SIZE))
    num_workers = int(cfg.get("num_workers", DEFAULT_NUM_WORKERS))
    train_loader, val_loader = create_train_val_loaders(
        train_df, val_df, raw_dir=raw_dir, batch_size=batch_size, num_workers=num_workers
    )

    # 3. Initialize model, loss, optimizer, and scheduler
    torch.manual_seed(seed + fold)
    model = build_model(
        num_classes=NUM_CLASSES,
        pretrained=True,
        dropout=float(cfg.get("dropout", 0.0)),
        device=device,
    )
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        model.head.parameters(),
        lr=float(cfg.get("learning_rate", 1e-3)),
        weight_decay=float(cfg.get("weight_decay", 1e-4)),
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        patience=int(cfg.get("reduce_lr_patience", DEFAULT_REDUCE_LR_PATIENCE)),
        factor=float(cfg.get("reduce_lr_factor", DEFAULT_REDUCE_LR_FACTOR)),
        min_lr=float(cfg.get("min_lr", DEFAULT_MIN_LR)),
    )

    # 4. Execute training loop with early stopping
    epochs = int(cfg.get("epochs", 30))
    fitted_model, history, duration = train_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=criterion,
        optimizer=optimizer,
        epochs=epochs,
        device=device,
        scheduler=scheduler,
        early_stopping_patience=cfg.get("early_stopping_patience", DEFAULT_EARLY_STOPPING_PATIENCE),
    )

    # 5. Evaluate final metrics on best weights
    val_loss, y_true, y_pred, y_probs = validate_epoch(fitted_model, val_loader, criterion, device)
    metrics = compute_metrics(y_true, y_pred, y_probs)
    metrics["val_loss"] = float(val_loss)
    logger.info("Validation Result [%s - Fold %d]: %s", drawing_type.upper(), fold, format_metrics(metrics))

    # 6. Log parameters and checkpoint to MLflow
    run_name = f"ResNet18_{drawing_type.capitalize()}_Fold{fold}"
    logged_params = {
        "drawing_type": drawing_type,
        "fold": fold,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": cfg.get("learning_rate", 1e-3),
        "weight_decay": cfg.get("weight_decay", 1e-4),
        "dropout": cfg.get("dropout", 0.0),
        "seed": seed,
        "device": str(device),
    }
    filename = model_filename or f"resnet18_{drawing_type}_fold{fold}.pt"
    model_path = log_training_run(
        run_name=run_name,
        drawing_type=drawing_type,
        model=fitted_model,
        params=logged_params,
        metrics=metrics,
        duration=duration,
        history=history,
        checkpoint_dir=checkpoint_dir,
        model_filename=filename,
        extra_tags={"fold": str(fold)},
    )

    return {
        "drawing_type": drawing_type,
        "fold": fold,
        "metrics": metrics,
        "duration": duration,
        "model_path": str(model_path),
    }


def train_modality_cv(
    drawing_type: str,
    master_manifest: pd.DataFrame,
    cfg: dict[str, Any],
    *,
    device: torch.device,
    folds: list[int] | tuple[int, ...] | None = None,
    checkpoint_dir: str | Path = MODELS_DIR,
    ) -> dict[str, Any]:

    """Train and evaluate a drawing modality across cross-validation folds."""
    target_folds = list(folds) if folds is not None else list(range(DEFAULT_CV_FOLDS))
    logger.info(
        ">>> Starting Cross-Validation for Modality: %s (%d Folds: %s) <<<",
        drawing_type.upper(),
        len(target_folds),
        target_folds,
    )

    fold_results: list[dict[str, Any]] = []
    for f in target_folds:
        res = train_single_drawing(
            drawing_type=drawing_type,
            master_manifest=master_manifest,
            cfg=cfg,
            device=device,
            fold=f,
            checkpoint_dir=checkpoint_dir,
        )
        fold_results.append(res)

    # Aggregate metric statistics across folds
    metric_keys = ["accuracy", "precision", "recall", "f1_score", "roc_auc", "val_loss"]
    cv_summary: dict[str, dict[str, float]] = {}
    for k in metric_keys:
        vals = [r["metrics"][k] for r in fold_results if k in r["metrics"]]
        if vals:
            mean_val = float(statistics.mean(vals))
            std_val = float(statistics.stdev(vals)) if len(vals) > 1 else 0.0
            cv_summary[k] = {"mean": mean_val, "std": std_val}

    # Select best fold (priority: roc_auc -> f1_score -> lowest val_loss)
    best_res = max(
        fold_results,
        key=lambda r: (
            r["metrics"].get("roc_auc", 0.0),
            r["metrics"].get("f1_score", 0.0),
            -r["metrics"].get("val_loss", float("inf")),
        ),
    )
    best_fold = best_res["fold"]

    # Copy best fold checkpoint to canonical resnet18_{drawing_type}.pt
    out_dir = Path(checkpoint_dir)
    canonical_model_path = out_dir / f"resnet18_{drawing_type}.pt"
    shutil.copy2(best_res["model_path"], canonical_model_path)
    logger.info(
        "Saved best fold checkpoint (Fold %d) to: %s",
        best_fold,
        canonical_model_path,
    )

    # Log summary report
    logger.info("================================================================================")
    logger.info("Cross-Validation Summary: %s (%d Folds)", drawing_type.upper(), len(target_folds))
    for r in fold_results:
        logger.info(
            "  Fold %d: %s | Loss: %.4f",
            r["fold"],
            format_metrics(r["metrics"]),
            r["metrics"].get("val_loss", 0.0),
        )
    logger.info("  ------------------------------------------------------------------------------")
    acc_stat = cv_summary.get("accuracy", {"mean": 0.0, "std": 0.0})
    f1_stat = cv_summary.get("f1_score", {"mean": 0.0, "std": 0.0})
    auc_stat = cv_summary.get("roc_auc", {"mean": 0.0, "std": 0.0})
    logger.info(
        "  Mean CV: Acc: %.4f ± %.4f | F1: %.4f ± %.4f | ROC-AUC: %.4f ± %.4f",
        acc_stat["mean"],
        acc_stat["std"],
        f1_stat["mean"],
        f1_stat["std"],
        auc_stat["mean"],
        auc_stat["std"],
    )
    logger.info("  Best Fold: Fold %d -> %s", best_fold, canonical_model_path.name)
    logger.info("================================================================================")

    return {
        "drawing_type": drawing_type,
        "folds": fold_results,
        "cv_summary": cv_summary,
        "best_fold": best_fold,
        "metrics": best_res["metrics"],
        "duration": sum(r["duration"] for r in fold_results),
        "model_path": str(canonical_model_path),
    }


def train_drawing_models(
    master_manifest: pd.DataFrame,
    cfg: dict[str, Any],
    drawing_types: list[str] | tuple[str, ...] | None = None,
    overrides: dict[str, Any] | None = None,
    ) -> dict[str, dict[str, Any]]:

    """Train ResNet-18 models across target drawing modalities."""
    config = dict(cfg)
    if overrides:
        config.update({k: v for k, v in overrides.items() if v is not None})

    setup_mlflow(
        tracking_uri=config.get("tracking_uri", MLFLOW_TRACKING_URI),
        experiment_name=config.get("experiment_name", MLFLOW_EXPERIMENT_NAME),
    )

    device = resolve_device(config.get("device", DEFAULT_DEVICE))
    target_drawings = drawing_types or config.get("drawing_types", ALL_DRAWING_TYPES)
    fold_param = config.get("fold", "all")
    checkpoint_dir = config.get("checkpoint_dir", MODELS_DIR)

    is_all_folds = fold_param is None or str(fold_param).strip().lower() == "all"

    results: dict[str, dict[str, Any]] = {}
    for dt in target_drawings:
        if is_all_folds:
            results[dt] = train_modality_cv(
                drawing_type=dt,
                master_manifest=master_manifest,
                cfg=config,
                device=device,
                checkpoint_dir=checkpoint_dir,
            )
        else:
            single_fold = int(fold_param)
            single_res = train_single_drawing(
                drawing_type=dt,
                master_manifest=master_manifest,
                cfg=config,
                device=device,
                fold=single_fold,
                checkpoint_dir=checkpoint_dir,
            )
            canonical_path = Path(checkpoint_dir) / f"resnet18_{dt}.pt"
            if Path(single_res["model_path"]) != canonical_path:
                shutil.copy2(single_res["model_path"], canonical_path)
            single_res["model_path"] = str(canonical_path)
            results[dt] = single_res

    logger.info("--------------------------------------------------")
    logger.info("Training Finished for %d Drawing Modalities", len(target_drawings))
    for dt, res in results.items():
        logger.info("%s: %s | Model: %s", dt.capitalize(), format_metrics(res["metrics"]), res["model_path"])
    logger.info("--------------------------------------------------")

    return results
