"""Subject-level metrics.

Image-level scores are not the quantity of interest. Each subject contributes
nine drawings, so an image-level average silently weights subjects by how many
files they happen to have, and it answers the wrong question: the product asks
"should this person be referred?", not "is this particular drawing abnormal?".

Predictions are therefore averaged per subject first, then scored. This is also
the objective Optuna will optimise in Phase 3, and it matches the metadata
baseline in `parkindraw.evaluation.baseline`, so all three numbers are directly
comparable.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)

# Locked by `3_PLAN.md` section 3.
DECISION_THRESHOLD = 0.5


def aggregate_by_subject(
    subject_ids: list[str] | np.ndarray,
    labels: list[int] | np.ndarray,
    probabilities: list[float] | np.ndarray,
) -> pd.DataFrame:
    """Average image-level probabilities into one score per subject."""
    frame = pd.DataFrame(
        {
            "subject_id": subject_ids,
            "label": labels,
            "probability": probabilities,
        }
    )
    subjects = frame.groupby("subject_id", as_index=False).agg(
        label=("label", "first"),
        probability=("probability", "mean"),
    )
    if frame.groupby("subject_id")["label"].nunique().max() > 1:
        raise ValueError("A subject carries more than one label")
    return subjects


def subject_metrics(
    subject_ids: list[str] | np.ndarray,
    labels: list[int] | np.ndarray,
    probabilities: list[float] | np.ndarray,
    *,
    threshold: float = DECISION_THRESHOLD,
) -> dict:
    """Score predictions at subject level.

    ROC-AUC is reported as None when the set holds a single class -- that
    happens in tiny smoke runs, and returning None keeps the result JSON-safe
    instead of raising or emitting NaN.
    """
    subjects = aggregate_by_subject(subject_ids, labels, probabilities)
    truth = subjects["label"].to_numpy()
    scores = subjects["probability"].to_numpy()
    predictions = (scores >= threshold).astype(int)

    both_classes = len(np.unique(truth)) == 2
    matrix = confusion_matrix(truth, predictions, labels=[0, 1])

    return {
        "subjects": int(len(subjects)),
        "roc_auc": round(float(roc_auc_score(truth, scores)), 4)
        if both_classes
        else None,
        "accuracy": round(float(accuracy_score(truth, predictions)), 4),
        "f1": round(float(f1_score(truth, predictions, zero_division=0)), 4),
        "threshold": threshold,
        "confusion_matrix": {
            "true_negative": int(matrix[0, 0]),
            "false_positive": int(matrix[0, 1]),
            "false_negative": int(matrix[1, 0]),
            "true_positive": int(matrix[1, 1]),
        },
    }


def summarise_folds(fold_metrics: list[dict], key: str = "roc_auc") -> dict:
    """Aggregate one metric across folds.

    The spread is reported next to the mean on purpose. With 53 development
    subjects a fold holds roughly 18 people, so a mean alone hides how unstable
    the estimate is.
    """
    values = [m[key] for m in fold_metrics if m.get(key) is not None]
    if not values:
        return {"mean": None, "std": None, "values": []}
    return {
        "mean": round(float(np.mean(values)), 4),
        "std": round(float(np.std(values)), 4),
        "values": [round(float(v), 4) for v in values],
    }
