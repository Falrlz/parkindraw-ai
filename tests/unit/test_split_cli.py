"""Tests for the split CLI and its temporary compatibility exports."""

from scripts import create_splits as cli

from parkindraw.data import splits as legacy_splits


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
    assert args.holdout_size == legacy_splits.DEFAULT_HOLDOUT_SIZE
    assert args.n_splits == legacy_splits.DEFAULT_N_SPLITS
    assert args.seed == legacy_splits.DEFAULT_SEED


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

    def fake_run_split(raw_dir, output_dir, **settings):
        calls.append((raw_dir, output_dir, settings))
        return split_summary()

    monkeypatch.setattr(cli, "run_split", fake_run_split)

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
    assert "Artifacts: custom-splits" in output


def test_legacy_module_reexports_the_canonical_cli_contract():
    assert vars(legacy_splits.build_argument_parser().parse_args([])) == vars(
        cli.build_argument_parser().parse_args([])
    )
