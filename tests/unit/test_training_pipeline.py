"""Unit tests for reusable training orchestration."""

from contextlib import contextmanager

import pytest

from parkindraw.pipelines import training
from parkindraw.training.config import TrainingConfig
from parkindraw.training.trainer import TrainingResult


def completed_training(config: TrainingConfig) -> TrainingResult:
    return TrainingResult(
        config={"drawing_type": config.drawing_type, "fold": config.fold},
        history=[{"epoch": 1, "accuracy": 0.75}],
        best_epoch=1,
        best_metrics={"accuracy": 0.75},
    )


def test_build_run_name_identifies_drawing_type_and_fold():
    config = TrainingConfig(drawing_type="meander", fold=2)

    assert training.build_run_name(config) == "meander-fold2"


def test_pipeline_without_tracker_trains_once_and_returns_run_context(
    monkeypatch,
    tmp_path,
):
    config = TrainingConfig(drawing_type="spiral", fold=1)
    expected_training = completed_training(config)
    calls = []

    def fake_train(received_config, checkpoint_path):
        calls.append((received_config, checkpoint_path))
        return expected_training

    monkeypatch.setattr(training, "train_fold", fake_train)

    result = training.run_training_pipeline(config, tmp_path, tracker=None)

    expected_checkpoint = tmp_path / "spiral-fold1.pt"
    assert calls == [(config, expected_checkpoint)]
    assert result == training.TrainingPipelineResult(
        run_name="spiral-fold1",
        checkpoint_path=expected_checkpoint,
        training=expected_training,
    )


def test_pipeline_with_tracker_records_the_completed_run_in_order(
    monkeypatch,
    tmp_path,
):
    config = TrainingConfig(drawing_type="circle", fold=0)
    expected_training = completed_training(config)
    events = []

    class FakeTracker:
        def configure(self):
            events.append(("configure",))

        @contextmanager
        def start_run(self, name, settings):
            events.append(("start", name, settings))
            yield
            events.append(("end",))

        def log_training_result(self, result, checkpoint_path):
            events.append(("result", result, checkpoint_path))

    def fake_train(received_config, checkpoint_path):
        events.append(("train", received_config, checkpoint_path))
        return expected_training

    monkeypatch.setattr(training, "train_fold", fake_train)

    result = training.run_training_pipeline(
        config,
        tmp_path,
        tracker=FakeTracker(),
    )

    assert [event[0] for event in events] == [
        "configure",
        "start",
        "train",
        "result",
        "end",
    ]
    assert events[1][1] == "circle-fold0"
    assert events[1][2]["drawing_type"] == "circle"
    assert events[1][2]["fold"] == 0
    assert events[2][2] == tmp_path / "circle-fold0.pt"
    assert events[3][1] is expected_training
    assert events[3][2] == tmp_path / "circle-fold0.pt"
    assert result.training is expected_training


def test_pipeline_does_not_hide_tracker_failures(monkeypatch, tmp_path):
    config = TrainingConfig()

    class FailingTracker:
        def configure(self):
            raise RuntimeError("tracking unavailable")

    def unexpected_train(*args, **kwargs):
        raise AssertionError("training must not start after tracking setup fails")

    monkeypatch.setattr(training, "train_fold", unexpected_train)

    with pytest.raises(RuntimeError, match="tracking unavailable"):
        training.run_training_pipeline(
            config,
            tmp_path,
            tracker=FailingTracker(),
        )
