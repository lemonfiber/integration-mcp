# Copyright (c) 2026 NightWorksIO
"""Splitting a mutation run across CI jobs, each module in exactly one."""

import fnmatch
from typing import TYPE_CHECKING

import pytest

from scripts import mutation_shard

if TYPE_CHECKING:
    import pathlib

PROJECT = """\
[tool.mutmut]
source_paths = ["src/"]
do_not_mutate = ["src/pkg/_generated/*"]
"""


def project(root: pathlib.Path) -> None:
    """Leave a project of four modules of different weights, and one that is not mutated."""
    (root / "pyproject.toml").write_text(PROJECT, encoding="utf-8")
    files = {
        "src/pkg/__init__.py": "# A comment.\n\nVALUE = 1\n",
        "src/pkg/heavy.py": "a = 1\n" * 30,
        "src/pkg/middle.py": "a = 1\n" * 20,
        "src/pkg/sub/light.py": "a = 1\n" * 5,
        "src/pkg/_generated/tools.py": "a = 1\n" * 99,
    }
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def test_every_mutated_module_is_in_exactly_one_shard_the_heaviest_spread_first(
    tmp_path: pathlib.Path,
) -> None:
    project(tmp_path)
    assert mutation_shard.shards(tmp_path, 2) == [["pkg.heavy"], ["pkg.middle", "pkg.sub.light", "pkg"]]


def test_a_shards_patterns_name_its_modules_mutants_and_no_others(tmp_path: pathlib.Path) -> None:
    project(tmp_path)
    taken = mutation_shard.patterns(["pkg", "pkg.sub.light"])

    def named(mutant: str) -> bool:
        return any(fnmatch.fnmatch(mutant, pattern) for pattern in taken)

    assert named("pkg.x_value__mutmut_1")
    assert named("pkg.xǁThingǁmethod__mutmut_2")
    assert named("pkg.sub.light.x_f__mutmut_3")
    assert not named("pkg.heavy.x_f__mutmut_1")
    assert not named("pkg.sub.x_f__mutmut_1")


def test_lines_of_code_leave_out_blanks_and_comments(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "module.py"
    path.write_text("# A comment.\n\n  # Indented.\nVALUE = 1\n", encoding="utf-8")
    assert mutation_shard.weight(path) == 1


def test_the_shard_named_is_printed(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    project(tmp_path)
    assert mutation_shard.run(tmp_path, ["0", "2"]) == 0
    assert capsys.readouterr().out == "pkg.heavy.x_* pkg.heavy.xǁ*\n"


@pytest.mark.parametrize("arguments", [[], ["1"], ["a", "2"], ["2", "2"]])
def test_a_shard_that_is_not_one_of_the_total_is_refused(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    arguments: list[str],
) -> None:
    project(tmp_path)
    assert mutation_shard.run(tmp_path, arguments) == 2
    assert capsys.readouterr().err


def test_the_project_is_split_whole() -> None:
    modules = [mutation_shard.module_of(path) for path in mutation_shard.mutated(mutation_shard.ROOT)]
    split = [module for shard in mutation_shard.shards(mutation_shard.ROOT, 5) for module in shard]
    assert sorted(split) == sorted(modules)
    assert "lemonfiber_mcp.web" in modules
    assert not any(module.startswith("lemonfiber_mcp._generated") for module in modules)
