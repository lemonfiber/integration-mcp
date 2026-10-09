# Copyright (c) 2026 NightWorksIO
"""Hold a mutation run to the minimum score `pyproject.toml` sets.

Reads what `mutmut export-cicd-stats` wrote. The score is the share of mutants
the suite told apart from the code it was written against: a mutant killed or
timed out counts, and one that survived, that no test reached, that was
suspicious or that crashed does not. A mutant the run did not try, being
another shard's, is not judged. A run that judged nothing is a failure rather
than a pass, since a score over no mutants says nothing about the suite.

    uv run python scripts/mutation_score.py
"""

import json
import pathlib
import sys
import tomllib
from typing import cast

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATS = pathlib.Path("mutants/mutmut-cicd-stats.json")


def minimum(root: pathlib.Path) -> float:
    """Return the minimum score, as a percentage, that `pyproject.toml` sets."""
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return float(project["tool"]["lemonfiber"]["mutation"]["minimum-score"])


DETECTED = ("killed", "timeout")
MISSED = ("survived", "no_tests", "suspicious", "segfault")
"""What a tried mutant came to: told apart from the code, or not."""


def score(stats: dict[str, int]) -> tuple[float, int, int]:
    """Return the score as a percentage, the mutants told apart, and the mutants judged."""
    detected = sum(stats.get(outcome, 0) for outcome in DETECTED)
    judged = detected + sum(stats.get(outcome, 0) for outcome in MISSED)
    return (100.0 * detected / judged if judged > 0 else 0.0), detected, judged


def run(root: pathlib.Path) -> int:
    """Compare the last run's score with the minimum, and say both."""
    path = root / STATS
    if not path.is_file():
        sys.stderr.write(
            f"::error::{STATS} is not there; run `mutmut run` and `mutmut export-cicd-stats` first.\n",
        )
        return 1
    stats = cast("dict[str, int]", json.loads(path.read_text(encoding="utf-8")))
    reached, detected, judged = score(stats)
    floor = minimum(root)
    line = (
        f"mutation score {reached:.2f}% ({detected} of {judged} mutants told apart; "
        f"{stats.get('survived', 0)} survived, {stats.get('no_tests', 0)} reached by no test), minimum {floor:.2f}%"
    )
    if judged == 0:
        sys.stderr.write("::error::the run judged no mutants, so it measured nothing.\n")
        return 1
    if reached < floor:
        sys.stderr.write(f"::error::{line}. Run `mutmut results` to see the mutants that survived.\n")
        return 1
    sys.stdout.write(f"{line}.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(run(ROOT))
