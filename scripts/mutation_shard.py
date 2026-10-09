# Copyright (c) 2026 NightWorksIO
"""Name the mutants one shard of a mutation run takes, so the run is split across CI jobs.

Every module mutmut mutates goes to exactly one shard, weighed by its lines of
code and spread so the shards weigh about the same. Prints the patterns
`mutmut run` takes, two for each module: its functions' mutants and its methods'.

    uv run mutmut run $(uv run python scripts/mutation_shard.py <index> <total>)
"""

import fnmatch
import pathlib
import sys
import tomllib
from typing import cast

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE_PREFIX = "src/"
FUNCTION = "x_"
METHOD = "xǁ"
"""How mutmut begins the name of a function's mutant, and of a method's, after the module's name."""
ARGUMENTS = ("index", "total")


def mutated(root: pathlib.Path) -> list[pathlib.Path]:
    """Return every source file mutmut mutates, as `pyproject.toml` sets out, relative to the root."""
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    settings = cast("dict[str, list[str]]", project["tool"]["mutmut"])
    skipped = settings.get("do_not_mutate", [])
    files = (
        path.relative_to(root)
        for source in settings["source_paths"]
        for path in sorted((root / source).rglob("*.py"))
    )
    return [
        path for path in files if not any(fnmatch.fnmatch(path.as_posix(), pattern) for pattern in skipped)
    ]


def module_of(path: pathlib.Path) -> str:
    """Return the module a source file holds, as mutmut names it."""
    dotted = path.as_posix().removeprefix(SOURCE_PREFIX).removesuffix(".py").replace("/", ".")
    return dotted.removesuffix(".__init__")


def weight(path: pathlib.Path) -> int:
    """Return a file's lines of code: neither blank nor a comment."""
    lines = (line.strip() for line in path.read_text(encoding="utf-8").splitlines())
    return sum(1 for line in lines if line and not line.startswith("#"))


def shards(root: pathlib.Path, total: int) -> list[list[str]]:
    """Return the modules of each shard, the heaviest placed first, each in the lightest shard so far."""
    weighed = sorted(
        ((weight(root / path), module_of(path)) for path in mutated(root)),
        key=lambda each: (-each[0], each[1]),
    )
    placed: list[list[str]] = [[] for _ in range(total)]
    loads = [0] * total
    for heft, module in weighed:
        lightest = loads.index(min(loads))
        placed[lightest].append(module)
        loads[lightest] += heft
    return placed


def patterns(modules: list[str]) -> list[str]:
    """Return the patterns naming every mutant of these modules."""
    return [f"{module}.{kind}*" for module in modules for kind in (FUNCTION, METHOD)]


def run(root: pathlib.Path, arguments: list[str]) -> int:
    """Print the patterns of the shard the arguments name, by its index from 0 and the number of shards."""
    if len(arguments) != len(ARGUMENTS) or not all(argument.isdigit() for argument in arguments):
        sys.stderr.write("usage: mutation_shard.py <index> <total>\n")
        return 2
    index, total = (int(argument) for argument in arguments)
    if not 0 <= index < total:
        sys.stderr.write(f"::error::shard {index} is not one of {total}.\n")
        return 2
    sys.stdout.write(" ".join(patterns(shards(root, total)[index])) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(run(ROOT, sys.argv[1:]))
