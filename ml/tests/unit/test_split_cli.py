"""Tests for the preparation pipeline CLI."""

from pathlib import Path

from pipelines import preparation as cli


def test_main_runs_preparation_pipeline(monkeypatch, capsys):
    calls = []

    def fake_run_pipeline(raw_dir, output_dir, holdout_size, seed):
        calls.append((raw_dir, output_dir, holdout_size, seed))
        return Path("custom-splits") / "master_manifest.csv"

    monkeypatch.setattr(cli, "run_preparation_pipeline", fake_run_pipeline)

    exit_code = cli.main(
        [
            "--raw-dir",
            "custom-raw",
            "--output-dir",
            "custom-splits",
            "--holdout-size",
            "0.25",
            "--seed",
            "7",
        ]
    )

    assert exit_code == 0
    assert calls == [("custom-raw", "custom-splits", 0.25, 7)]
    output = capsys.readouterr().out
    assert "Master manifest successfully created:" in output
