# Copyright (c) 2026 NightWorksIO
"""The rules the tree is built to: the stack is reached through sdk-python alone, with a key and never a password.

The certificates reach the network for themselves, to probe this server and to
obtain a certificate, and never import what reaches the stack.
"""

import ast
import importlib.metadata
import pathlib
import re
import sys
import tomllib
from typing import Final

import pytest

from lemonfiber_mcp import catalogue, settings

ROOT: Final = pathlib.Path(__file__).resolve().parent.parent
SERVER: Final = ROOT / "src" / "lemonfiber_mcp"
VENDOR: Final = SERVER / "_vendor"
CERTIFICATES: Final = SERVER / "certificates"
SHARED_GATE: Final = ROOT / "scripts" / "no_open_codeql_alert.py"

SUPPRESSIONS: Final = re.compile(
    r"#\s*(type:\s*ignore|pyright:|noqa|pragma:\s*no\s*(cover|branch))",
    re.IGNORECASE,
)
WIRE: Final = frozenset(
    {
        "aiohttp",
        "urllib3",
        "requests",
        "httpx",
        "httpx2",
        "http.client",
        "urllib.request",
        "socket",
        "websockets",
    },
)
"""Every way to reach a stack that is not sdk-python, by the module a file would import."""
STACK: Final = frozenset(
    {"lemonfiber", "lemonfiber_mcp.connection", "lemonfiber_mcp.stack", "lemonfiber_mcp.web"},
)
"""What holds a key or reaches the stack, by the module a file would import."""
PASSWORD: Final = re.compile(r"passw(or)?d", re.IGNORECASE)


def python_files(*roots: pathlib.Path) -> list[pathlib.Path]:
    """Return every Python file under these roots but the vendored client and the shared gate's copy."""
    return sorted(
        path
        for root in roots
        for path in root.rglob("*.py")
        if path != SHARED_GATE and VENDOR not in path.parents
    )


def imported(path: pathlib.Path) -> set[str]:
    """Return every module a file imports, by its full dotted name and by each prefix of it."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        modules: list[str] = []
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module is not None and node.level == 0:
            modules = [node.module, *(f"{node.module}.{alias.name}" for alias in node.names)]
        for module in modules:
            parts = module.split(".")
            names.update(".".join(parts[: end + 1]) for end in range(len(parts)))
    return names


@pytest.mark.parametrize("path", python_files(SERVER, ROOT / "tests", ROOT / "scripts"), ids=str)
def test_nothing_silences_a_checker(path: pathlib.Path) -> None:
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        assert not SUPPRESSIONS.search(line), f"{path}:{number} silences a checker"


@pytest.mark.parametrize(
    "path",
    [path for path in python_files(SERVER) if CERTIFICATES not in path.parents],
    ids=str,
)
def test_the_stack_is_reached_through_sdk_python_alone(path: pathlib.Path) -> None:
    assert not imported(path) & WIRE, f"{path} reaches past sdk-python"


@pytest.mark.parametrize("path", python_files(CERTIFICATES), ids=str)
def test_the_certificates_reach_the_network_without_the_stack_or_a_key(path: pathlib.Path) -> None:
    assert not imported(path) & STACK, f"{path} reaches the stack"


@pytest.mark.parametrize("path", python_files(SERVER), ids=str)
def test_no_password_is_asked_for_or_exchanged(path: pathlib.Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    used = imported(path) | {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    used |= {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert not used & {"admit", "admit_async", "lemonfiber.admit", "lemonfiber.admit_async"}, path


def test_no_tool_takes_a_password() -> None:
    for shape in catalogue.SHAPES.values():
        assert not any(PASSWORD.search(name) for name in shape.parameters), shape.name


def test_no_setting_takes_a_password() -> None:
    names = [value for key, value in vars(settings).items() if key.isupper() and isinstance(value, str)]
    assert names
    assert not any(PASSWORD.search(name) for name in names)


@pytest.mark.parametrize("path", python_files(SERVER), ids=str)
def test_no_module_declares_a_response_shape(path: pathlib.Path) -> None:
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ClassDef):
            assert not {ast.unparse(base) for base in node.bases} & {"TypedDict", "typing.TypedDict"}, path


def declared() -> set[str]:
    """Return every distribution `pyproject.toml` names as the server's own dependency, by its normalised name."""
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    return {
        re.split(r"[<>=!~\[ ;]", requirement, maxsplit=1)[0].lower()
        for requirement in project["dependencies"]
    }


@pytest.mark.parametrize("path", python_files(SERVER), ids=str)
def test_every_package_the_server_imports_is_declared(path: pathlib.Path) -> None:
    distributions = importlib.metadata.packages_distributions()
    tops = (
        {name.split(".")[0] for name in imported(path)}
        - set(sys.stdlib_module_names)
        - {"lemonfiber_mcp", "lemonfiber"}
    )
    for top in tops:
        assert {name.lower() for name in distributions.get(top, [top])} & declared(), (
            f"{path} imports {top} undeclared"
        )
