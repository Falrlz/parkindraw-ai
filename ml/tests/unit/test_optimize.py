"""Unit tests for the Optuna objective."""

import optuna
import pytest

from parkindraw.training.config import TrainingConfig
from parkindraw.training.optimization_config import OptimizationConfig
from parkindraw.training.optimize import (
    OptimizationError,
    build_trial_config,
    evaluate_trial,
    suggest_hyperparameters,
)
from parkindraw.training.trainer import TrainingResult


class FakeTrial:
    def __init__(self, *, prune_after_step=None):
        self.number = 0
        self.params = {}
        self.user_attrs = {}
        self.reports = []
        self.prune_after_step = prune_after_step

    def suggest_float(self, name, low, high, *, log=False, step=None):
        value = low if step is None else low + step
        self.params[name] = value
        return value

    def suggest_categorical(self, name, choices):
        value = choices[0]
        self.params[name] = value
        return value

    def set_user_attr(self, name, value):
        self.user_attrs[name] = value

    def report(self, value, step):
        self.reports.append((value, step))

    def should_prune(self):
        return self.prune_after_step is not None and (
            self.reports[-1][1] >= self.prune_after_step
        )


def training_result(roc_auc, accuracy=0.7, f1=0.6):
    return TrainingResult(
        config={},
        history=[
            {
                "epoch": 1,
                "train_loss": 0.5,
                "validation_loss": 0.6,
                "roc_auc": roc_auc,
            }
        ],
        best_epoch=1,
        best_metrics={"roc_auc": roc_auc, "accuracy": accuracy, "f1": f1},
    )


def test_suggest_hyperparameters_uses_the_recorded_search_space():
    config = OptimizationConfig()
    trial = FakeTrial()

    parameters = suggest_hyperparameters(trial, config)

    assert set(parameters) == {
        "learning_rate",
        "weight_decay",
        "dropout",
        "batch_size",
    }
    assert parameters["batch_size"] in config.batch_sizes
    assert config.dropout_low <= parameters["dropout"] <= config.dropout_high


def test_build_trial_config_preserves_base_and_applies_trial_values():
    base = TrainingConfig(drawing_type="spiral", fold=0, epochs=4)
    parameters = {
        "learning_rate": 1e-4,
        "weight_decay": 1e-5,
        "dropout": 0.2,
        "batch_size": 8,
    }

    result = build_trial_config(base, "circle", 2, parameters)

    assert base.drawing_type == "spiral"
    assert base.fold == 0
    assert result.drawing_type == "circle"
    assert result.fold == 2
    assert result.epochs == 4
    assert result.dropout == 0.2


def test_trial_objective_is_mean_subject_roc_auc_across_folds():
    config = OptimizationConfig(n_splits=3)
    trial = FakeTrial()
    seen_configs = []
    scores = iter([0.6, 0.7, 0.8])

    def fake_train(fold_config):
        seen_configs.append(fold_config)
        return training_result(next(scores))

    objective = evaluate_trial(
        trial,
        TrainingConfig(),
        config,
        "meander",
        train=fake_train,
    )

    assert objective == pytest.approx(0.7)
    assert [item.fold for item in seen_configs] == [0, 1, 2]
    assert {item.drawing_type for item in seen_configs} == {"meander"}
    assert trial.reports[-1] == pytest.approx((0.7, 2))
    assert len(trial.user_attrs["fold_metrics"]) == 3
    assert trial.user_attrs["fold_metrics"][0]["history"][0]["epoch"] == 1
    assert trial.user_attrs["mean_accuracy"] == pytest.approx(0.7)


def test_pruned_trial_stops_before_later_folds():
    trial = FakeTrial(prune_after_step=0)
    calls = []

    def fake_train(config):
        calls.append(config.fold)
        return training_result(0.6)

    with pytest.raises(optuna.TrialPruned, match="pruned after fold 0"):
        evaluate_trial(
            trial,
            TrainingConfig(),
            OptimizationConfig(n_splits=3),
            "spiral",
            train=fake_train,
        )

    assert calls == [0]
    assert len(trial.user_attrs["fold_metrics"]) == 1


def test_missing_roc_auc_fails_instead_of_becoming_a_fake_score():
    def fake_train(config):
        return training_result(None)

    with pytest.raises(OptimizationError, match="produced no ROC-AUC"):
        evaluate_trial(
            FakeTrial(),
            TrainingConfig(),
            OptimizationConfig(n_splits=2),
            "circle",
            train=fake_train,
        )
