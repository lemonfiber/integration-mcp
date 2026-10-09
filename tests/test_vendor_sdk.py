# Copyright (c) 2026 NightWorksIO
"""Vendoring sdk-python and its contract at one commit, and finding a copy that moved."""

import subprocess
from typing import TYPE_CHECKING

import pytest

from scripts import vendor_sdk

if TYPE_CHECKING:
    import pathlib

PACKAGE = {"__init__.py": b"from lemonfiber.client import Client\n", "client.py": b"class Client: ...\n"}
CONTRACT = {"VERSION": b"0" * 40 + b"\n", "web-api/index.json": b'{"api_version": 1}\n'}


def git(where: pathlib.Path, *arguments: str) -> str:
    """Run git in a directory and return what it printed."""
    return subprocess.run(
        ["git", "-C", str(where), *arguments],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()


def commit(sdk: pathlib.Path, files: dict[str, bytes], message: str) -> str:
    """Write files into the stand-in sdk-python, commit them, and return the commit."""
    for path, content in files.items():
        (sdk / path).parent.mkdir(parents=True, exist_ok=True)
        (sdk / path).write_bytes(content)
    git(sdk, "add", "-A")
    git(
        sdk,
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "-c",
        "commit.gpgsign=false",
        "-c",
        "core.hooksPath=/dev/null",
        "commit",
        "-qm",
        message,
    )
    return git(sdk, "rev-parse", "HEAD")


@pytest.fixture
def sdk(tmp_path: pathlib.Path) -> pathlib.Path:
    """Return a stand-in sdk-python repository whose `main` holds the package and the contract."""
    repository = tmp_path / "sdk-python"
    repository.mkdir()
    git(repository, "init", "-q", "-b", "main")
    commit(
        repository,
        {
            **{f"src/lemonfiber/{name}": content for name, content in PACKAGE.items()},
            **{f"contract/{name}": content for name, content in CONTRACT.items()},
        },
        "the package and its contract",
    )
    return repository


@pytest.fixture
def tree(tmp_path: pathlib.Path) -> pathlib.Path:
    """Return an empty tree for the copies to land in."""
    root = tmp_path / "server"
    root.mkdir()
    return root


def take(sdk: pathlib.Path, tree: pathlib.Path, revision: str) -> int:
    """Vendor a commit of the stand-in into the tree."""
    return vendor_sdk.run(["take", revision], tree, str(sdk))


def check(sdk: pathlib.Path, tree: pathlib.Path) -> int:
    """Check the tree's copies against the stand-in."""
    return vendor_sdk.run(["check"], tree, str(sdk))


def vendored(sdk: pathlib.Path, tree: pathlib.Path) -> pathlib.Path:
    """Vendor the stand-in's head and return the package's copy."""
    assert take(sdk, tree, git(sdk, "rev-parse", "HEAD")) == 0
    return tree / vendor_sdk.COPY


def test_a_commit_is_vendored_byte_for_byte_beside_its_revision(
    sdk: pathlib.Path,
    tree: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    head = git(sdk, "rev-parse", "HEAD")
    assert take(sdk, tree, head) == 0
    copy = tree / vendor_sdk.COPY
    assert {path.name: path.read_bytes() for path in copy.iterdir() if path.name != "REVISION"} == PACKAGE
    assert vendor_sdk.held(tree, vendor_sdk.CONTRACT) == CONTRACT
    assert (tree / vendor_sdk.REVISION).read_text(encoding="ascii") == f"{head}\n"
    said = capsys.readouterr().out
    assert "2 files in src/lemonfiber_mcp/_vendor/lemonfiber" in said
    assert "2 files in contract" in said
    assert check(sdk, tree) == 0
    assert f"the copies are sdk-python {head}" in capsys.readouterr().out


def test_taking_a_commit_replaces_both_copies_whole(sdk: pathlib.Path, tree: pathlib.Path) -> None:
    first = git(sdk, "rev-parse", "HEAD")
    git(sdk, "rm", "-q", "src/lemonfiber/client.py", "contract/VERSION")
    second = commit(
        sdk,
        {"src/lemonfiber/stream.py": b"STREAM = 1\n", "contract/web-api/reads.json": b"[]\n"},
        "a module and a list move",
    )
    assert take(sdk, tree, first) == 0
    assert take(sdk, tree, second) == 0
    assert sorted(path.name for path in (tree / vendor_sdk.COPY).iterdir()) == [
        "REVISION",
        "__init__.py",
        "stream.py",
    ]
    assert sorted(vendor_sdk.held(tree, vendor_sdk.CONTRACT)) == ["web-api/index.json", "web-api/reads.json"]


@pytest.mark.parametrize("revision", ["main", "4a1dd3a", "z" * 40])
def test_what_is_not_a_full_commit_is_refused(sdk: pathlib.Path, tree: pathlib.Path, revision: str) -> None:
    assert take(sdk, tree, revision) == 1
    assert not (tree / vendor_sdk.COPY).exists()


@pytest.mark.parametrize("gone", ["src", "contract"])
def test_a_commit_without_either_tree_is_refused_and_writes_nothing(
    sdk: pathlib.Path,
    tree: pathlib.Path,
    gone: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    git(sdk, "rm", "-rq", gone)
    without = commit(sdk, {"README.md": b"gone\n"}, f"{gone} goes")
    assert take(sdk, tree, without) == 1
    assert f"has no {gone}" in capsys.readouterr().err
    assert not (tree / vendor_sdk.COPY).exists()
    assert not (tree / vendor_sdk.CONTRACT).exists()


def test_a_commit_the_repository_does_not_have_is_refused(sdk: pathlib.Path, tree: pathlib.Path) -> None:
    assert take(sdk, tree, "0" * 40) == 1


def test_a_repository_that_cannot_be_cloned_is_refused(
    tmp_path: pathlib.Path,
    tree: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert take(tmp_path / "nowhere", tree, "0" * 40) == 1
    assert "could not be cloned" in capsys.readouterr().err


def test_a_hand_edit_to_the_package_is_found(
    sdk: pathlib.Path,
    tree: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (vendored(sdk, tree) / "client.py").write_bytes(b"class Client: pass\n")
    assert check(sdk, tree) == 1
    assert "client.py differs" in capsys.readouterr().err


def test_a_hand_edit_to_the_contract_is_found(
    sdk: pathlib.Path,
    tree: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    vendored(sdk, tree)
    (tree / vendor_sdk.CONTRACT / "web-api/index.json").write_bytes(b'{"api_version": 2}\n')
    assert check(sdk, tree) == 1
    assert "contract is not sdk-python" in capsys.readouterr().err


def test_a_file_gone_from_the_copy_is_found(
    sdk: pathlib.Path,
    tree: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (vendored(sdk, tree) / "client.py").unlink()
    assert check(sdk, tree) == 1
    assert "client.py is missing" in capsys.readouterr().err


def test_a_file_added_to_the_copy_is_found(
    sdk: pathlib.Path,
    tree: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (vendored(sdk, tree) / "extra.py").write_bytes(b"\n")
    assert check(sdk, tree) == 1
    assert "extra.py is not in sdk-python" in capsys.readouterr().err


def test_compiled_files_beside_the_copy_are_not_part_of_it(sdk: pathlib.Path, tree: pathlib.Path) -> None:
    cache = vendored(sdk, tree) / "__pycache__"
    cache.mkdir()
    (cache / "client.cpython-314.pyc").write_bytes(b"\0")
    assert check(sdk, tree) == 0


@pytest.mark.parametrize("moved", ["src/lemonfiber/client.py", "contract/web-api/index.json"])
def test_main_changing_either_tree_is_drift(
    sdk: pathlib.Path,
    tree: pathlib.Path,
    moved: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    vendored(sdk, tree)
    head = commit(sdk, {moved: b"changed\n"}, "it changes")
    assert check(sdk, tree) == 1
    said = capsys.readouterr().err
    assert f"changed {moved}" in said
    assert f"take {head}" in said


def test_main_changing_only_what_is_not_shipped_is_not_drift(sdk: pathlib.Path, tree: pathlib.Path) -> None:
    vendored(sdk, tree)
    commit(sdk, {"tests/test_client.py": b"\n"}, "a test arrives")
    assert check(sdk, tree) == 0


def test_a_copy_naming_no_commit_is_refused(
    sdk: pathlib.Path,
    tree: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (vendored(sdk, tree) / "REVISION").unlink()
    assert check(sdk, tree) == 1
    assert "names no commit" in capsys.readouterr().err


def test_a_copy_naming_something_else_is_refused(
    sdk: pathlib.Path,
    tree: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (vendored(sdk, tree) / "REVISION").write_text("main\n", encoding="ascii")
    assert check(sdk, tree) == 1
    assert "not a full commit hash" in capsys.readouterr().err


def test_the_copy_in_this_tree_names_a_full_commit() -> None:
    assert vendor_sdk.COMMIT.fullmatch(vendor_sdk.recorded(vendor_sdk.ROOT))
