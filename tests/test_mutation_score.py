# Copyright (c) 2026 NightWorksIO
"""Holding a mutation run to the minimum score."""

import json
from typing import TYPE_CHECKING

from scripts import mutation_score

if TYPE_CHECKING:
    import pathlib

    import pytest


def write_score(root: pathlib.Path, stats: dict[str, int], minimum: int = 90) -> None:
    """Leave a mutation run's stats and a minimum where the score script reads them."""
    (root / "mutants").mkdir()
    (root / "mutants/mutmut-cicd-stats.json").write_text(json.dumps(stats), encoding="utf-8")
    (root / "pyproject.toml").write_text(
        f"[tool.lemonfiber.mutation]\nminimum-score = {minimum}\n",
        encoding="utf-8",
    )


def test_a_score_at_the_minimum_passes(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_score(tmp_path, {"total": 12, "skipped": 2, "killed": 8, "timeout": 1, "survived": 1})
    assert mutation_score.run(tmp_path) == 0
    assert "mutation score 90.00% (9 of 10" in capsys.readouterr().out


def test_a_score_below_the_minimum_fails(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_score(tmp_path, {"total": 10, "killed": 8, "survived": 1, "no_tests": 1})
    assert mutation_score.run(tmp_path) == 1
    assert "80.00%" in capsys.readouterr().err


def test_a_run_judging_no_mutants_fails(tmp_path: pathlib.Path) -> None:
    write_score(tmp_path, {"total": 3, "skipped": 3})
    assert mutation_score.run(tmp_path) == 1


def test_no_run_fails(tmp_path: pathlib.Path) -> None:
    assert mutation_score.run(tmp_path) == 1


def test_the_minimum_is_the_projects() -> None:
    assert mutation_score.minimum(mutation_score.ROOT) > 0
