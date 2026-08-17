"""Tests for the split / data preparation CLI."""

from pathlib import Path

from scripts import create_splits as cli

from parkindraw.data import splits as core_splits
from parkindraw.pipelines.data_preparation import DataPreparationResult


def split_summary():
    """Return a lightweight stand-in for generated split metadata."""
    return {
        "total_subjects": 10,
        "development_subjects": 8,
        "holdout_subjects": 2,
        "n_splits": 3,
        "sessions": 8,
        "duplicate_clusters": [["1", "2"]],
    }


def test_parser_defaults_match_the_project_split_defaults():
    args = cli.build_argument_parser().parse_args([])

    assert args.raw_dir == "data/raw"
    assert args.output_dir == "data/splits"
    assert args.holdout_size == core_splits.DEFAULT_HOLDOUT_SIZE
    assert args.n_splits == core_splits.DEFAULT_N_SPLITS
    assert args.seed == core_splits.DEFAULT_SEED


def test_parser_accepts_every_supported_override():
    args = cli.build_argument_parser().parse_args(
        [
            "--raw-dir",
            "custom-raw",
            "--output-dir",
            "custom-splits",
            "--holdout-size",
            "0.25",
            "--n-splits",
            "5",
            "--seed",
            "7",
        ]
    )

    assert vars(args) == {
        "raw_dir": "custom-raw",
        "output_dir": "custom-splits",
        "holdout_size": 0.25,
        "n_splits": 5,
        "seed": 7,
    }


def test_main_runs_split_generation_and_prints_summary(monkeypatch, capsys):
    calls = []

    def fake_run_pipeline(raw_dir, output_dir, **settings):
        calls.append((raw_dir, output_dir, settings))
        out = Path(output_dir)
        return DataPreparationResult(
            summary=split_summary(),
            output_dir=out,
            master_manifest_path=out / "master_manifest.csv",
            sessions_path=out / "sessions.csv",
            split_config_path=out / "split_config.json",
        )

    monkeypatch.setattr(cli, "run_data_preparation_pipeline", fake_run_pipeline)

    exit_code = cli.main(
        [
            "--raw-dir",
            "custom-raw",
            "--output-dir",
            "custom-splits",
            "--holdout-size",
            "0.25",
            "--n-splits",
            "5",
            "--seed",
            "7",
        ]
    )

    assert exit_code == 0
    assert calls == [
        (
            "custom-raw",
            "custom-splits",
            {"holdout_size": 0.25, "n_splits": 5, "seed": 7},
        )
    ]
    output = capsys.readouterr().out
    assert "10 subjects (8 development, 2 holdout)" in output
    assert "3 folds, 8 sessions" in output
    assert "Duplicate clusters merged: 1" in output
    assert "Master manifest:" in output
