"""Tests for the baseline CLI and its temporary compatibility exports."""

from scripts import evaluate_baseline as cli

from parkindraw.evaluation import baseline as core_baseline


def baseline_summary():
    """Return a lightweight stand-in for baseline evaluation output."""
    return {
        "results": {
            "circle": {
                "mean_auc": 0.7,
                "std_auc": 0.1,
                "fold_auc": [0.6, 0.7, 0.8],
            },
            "spiral": {
                "mean_auc": 0.8,
                "std_auc": 0.05,
                "fold_auc": [0.75, 0.8, 0.85],
            },
        },
        "highest_mean_auc": 0.8,
    }


def test_parser_defaults_match_the_project_baseline_defaults():
    args = cli.build_argument_parser().parse_args([])

    assert args.raw_dir == "data/raw"
    assert args.splits_dir == "data/splits"
    assert args.output == "reports/metadata_baseline.json"
    assert args.n_splits == core_baseline.DEFAULT_N_SPLITS
    assert args.seed == core_baseline.DEFAULT_SEED


def test_parser_accepts_every_supported_override():
    args = cli.build_argument_parser().parse_args(
        [
            "--raw-dir",
            "custom-raw",
            "--splits-dir",
            "custom-splits",
            "--output",
            "custom-report.json",
            "--n-splits",
            "5",
            "--seed",
            "7",
        ]
    )

    assert vars(args) == {
        "raw_dir": "custom-raw",
        "splits_dir": "custom-splits",
        "output": "custom-report.json",
        "n_splits": 5,
        "seed": 7,
    }


def test_main_runs_baseline_evaluation_and_prints_summary(monkeypatch, capsys):
    calls = []

    def fake_run_baseline(raw_dir, splits_dir, output, **settings):
        calls.append((raw_dir, splits_dir, output, settings))
        return baseline_summary()

    monkeypatch.setattr(cli, "run_baseline", fake_run_baseline)

    exit_code = cli.main(
        [
            "--raw-dir",
            "custom-raw",
            "--splits-dir",
            "custom-splits",
            "--output",
            "custom-report.json",
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
            "custom-report.json",
            {"n_splits": 5, "seed": 7},
        )
    ]
    output = capsys.readouterr().out
    assert "Metadata-only baseline (subject-level ROC-AUC)" in output
    assert "circle  : 0.700 +/- 0.100" in output
    assert "spiral  : 0.800 +/- 0.050" in output
    assert "Any model must clearly exceed 0.800" in output
    assert "Report: custom-report.json" in output
