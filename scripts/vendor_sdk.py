# Copyright (c) 2026 NightWorksIO
"""Vendor sdk-python at one commit, and check the copy against that commit and against `main`.

The server reaches a stack only through sdk-python, taken by commit rather than
from a registry, and generates its tools from the contract that same commit
was generated from. `take` copies the commit's `src/lemonfiber/` into
`src/lemonfiber_mcp/_vendor/lemonfiber/` and its `contract/` into `contract/`,
byte for byte, and records the commit in `REVISION` beside the package, the
file sdk-python's backward-compatibility check reads. `check` fails when either
copy is not that commit's tree, or when sdk-python's `main` has changed what
either holds since.

    python3 scripts/vendor_sdk.py take <commit>
    python3 scripts/vendor_sdk.py check

Each reads sdk-python from a bare clone of its repository made for the run.
"""

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable

ROOT: Final = pathlib.Path(__file__).resolve().parent.parent
SDK: Final = "https://github.com/lemonfiber/sdk-python.git"
VENDOR: Final = pathlib.Path("src/lemonfiber_mcp/_vendor")
COPY: Final = VENDOR / "lemonfiber"
REVISION: Final = COPY / "REVISION"
"""The commit both copies were taken from, where sdk-python's backward-compatibility check reads it."""
CONTRACT: Final = pathlib.Path("contract")
TREES: Final = {"src/lemonfiber": COPY, "contract": CONTRACT}
"""Each directory taken from sdk-python, to where it is copied here."""
TRUNK: Final = "main"
COMMIT: Final = re.compile(r"^[0-9a-f]{40}$")
BLOB: Final = "blob"

type Git = Callable[..., bytes]
"""Run git in the sdk-python clone with these arguments and return what it wrote."""


class VendorError(Exception):
    """The copy could not be taken, or does not hold what it should."""


def git_in(clone: pathlib.Path) -> Git:
    """Return a runner for git commands in a clone."""

    def run(*arguments: str) -> bytes:
        done = subprocess.run(
            ["git", "-C", str(clone), *arguments],
            capture_output=True,
            check=False,
        )
        if done.returncode != 0:
            said = done.stderr.decode(errors="replace").strip()
            msg = f"git {' '.join(arguments)} failed: {said}"
            raise VendorError(msg)
        return done.stdout

    return run


def tree(git: Git, commit: str, source: str) -> dict[str, bytes]:
    """Return every file under one directory at a commit, by its path inside it, as the bytes it is."""
    if not COMMIT.fullmatch(commit):
        msg = f"{commit!r} is not a full commit hash."
        raise VendorError(msg)
    listing = git("ls-tree", "-r", "-z", commit, "--", f"{source}/").decode()
    files: dict[str, bytes] = {}
    for entry in filter(None, listing.split("\0")):
        mode_type_object, path = entry.split("\t", 1)
        object_name = mode_type_object.split(" ")[2]
        files[path.removeprefix(f"{source}/")] = git("cat-file", BLOB, object_name)
    if not files:
        msg = f"sdk-python {commit} has no {source}/."
        raise VendorError(msg)
    return files


def held(root: pathlib.Path, copy: pathlib.Path) -> dict[str, bytes]:
    """Return every file of one copy, by its path inside it, leaving out `REVISION`."""
    where = root / copy
    return {
        path.relative_to(where).as_posix(): path.read_bytes()
        for path in sorted(where.rglob("*"))
        if path.is_file() and path != root / REVISION and "__pycache__" not in path.parts
    }


def recorded(root: pathlib.Path) -> str:
    """Return the commit the copy records, refusing a record that is not one."""
    path = root / REVISION
    if not path.is_file():
        msg = f"{REVISION} is not there, so the copy names no commit."
        raise VendorError(msg)
    commit = path.read_text(encoding="ascii").strip()
    if not COMMIT.fullmatch(commit):
        msg = f"{REVISION} holds {commit!r}, which is not a full commit hash."
        raise VendorError(msg)
    return commit


def take(root: pathlib.Path, git: Git, commit: str) -> list[str]:
    """Replace both copies with what a commit holds, record the commit, and say what was written."""
    taken = {source: tree(git, commit, source) for source in TREES}
    said: list[str] = []
    for source, copy in TREES.items():
        where = root / copy
        if where.exists():
            shutil.rmtree(where)
        for path, content in taken[source].items():
            target = where / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        said.append(f"vendored sdk-python {commit} {source}/: {len(taken[source])} files in {copy}.")
    (root / REVISION).write_text(f"{commit}\n", encoding="ascii")
    return said


def differences(expected: dict[str, bytes], found: dict[str, bytes]) -> list[str]:
    """Return each path where a copy differs from what it should hold."""
    return [
        *(f"{path} is missing" for path in sorted(expected.keys() - found.keys())),
        *(f"{path} is not in sdk-python" for path in sorted(found.keys() - expected.keys())),
        *(
            f"{path} differs"
            for path in sorted(expected.keys() & found.keys())
            if expected[path] != found[path]
        ),
    ]


def check(root: pathlib.Path, git: Git) -> list[str]:
    """Return every fault of the copies: unlike their commit's tree, or behind what `main` ships."""
    commit = recorded(root)
    faults = [
        f"{copy} is not sdk-python {commit} {source}/: {one}"
        for source, copy in TREES.items()
        for one in differences(tree(git, commit, source), held(root, copy))
    ]
    head = git("rev-parse", TRUNK).decode().strip()
    moved = (
        git("diff", "--name-only", commit, head, "--", *(f"{source}/" for source in TREES)).decode().split()
    )
    if moved:
        faults.append(
            f"sdk-python {TRUNK} ({head}) changed {', '.join(moved)} since {commit}. "
            f"Run `python3 scripts/vendor_sdk.py take {head}`, then `just generate`, and commit the result.",
        )
    return faults


def cloned(destination: pathlib.Path, source: str) -> pathlib.Path:
    """Return a bare clone of sdk-python made in a directory."""
    clone = destination / "sdk-python.git"
    done = subprocess.run(
        ["git", "clone", "--bare", "--quiet", "--", source, str(clone)],
        capture_output=True,
        check=False,
    )
    if done.returncode != 0:
        msg = f"sdk-python could not be cloned from {source}: {done.stderr.decode(errors='replace').strip()}"
        raise VendorError(msg)
    return clone


def run(arguments: list[str], root: pathlib.Path = ROOT, source: str = SDK) -> int:
    """Take or check the copies as the arguments say, reading sdk-python from `source`, and say what was found."""
    parser = argparse.ArgumentParser(description="Vendor sdk-python at one commit, and check the copy.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="check the copies against their commit and against main")
    taking = commands.add_parser("take", help="replace the copies with what a commit holds")
    taking.add_argument("commit")
    asked = parser.parse_args(arguments)
    with tempfile.TemporaryDirectory() as scratch:
        try:
            git = git_in(cloned(pathlib.Path(scratch), source))
            said = take(root, git, asked.commit) if asked.command == "take" else check(root, git)
        except VendorError as fault:
            sys.stderr.write(f"::error::{fault}\n")
            return 1
    if asked.command == "check":
        for fault in said:
            sys.stderr.write(f"::error::{fault}\n")
        if said:
            return 1
        said = [
            f"the copies are sdk-python {recorded(root)}, and {TRUNK} has changed nothing they hold since.",
        ]
    for line in said:
        sys.stdout.write(f"{line}\n")
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
