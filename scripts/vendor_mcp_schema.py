# Copyright (c) 2026 NightWorksIO
"""Vendor the MCP specification's own schema at one revision, a definition a file.

The conformance suite holds every tool, resource and answer the server writes
to the schema the specification publishes, for each protocol version the
server speaks. Each version's `schema.json` is longer than a reviewer can read,
so it is kept as `index.json`, holding everything but the definitions, beside
one file per definition; `assembled` puts the document back together, and its
references, all within the document, resolve as they did.

    python3 scripts/vendor_mcp_schema.py take <revision>

The revision is recorded in `vendor/mcp-schema/REVISION`.
"""

import json
import pathlib
import re
import shutil
import sys
import urllib.request
from typing import TYPE_CHECKING, Final, cast

if TYPE_CHECKING:
    from collections.abc import Callable

ROOT: Final = pathlib.Path(__file__).resolve().parent.parent
VENDOR: Final = pathlib.Path("vendor/mcp-schema")
VERSIONS: Final = ("2025-11-25", "2026-07-28")
"""The protocol versions the server speaks, each of whose schema is vendored."""
SOURCE: Final = "https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/{revision}/schema/{version}/schema.json"
COMMIT: Final = re.compile(r"^[0-9a-f]{40}$")
DEFINITIONS: Final = "$defs"
INDEX: Final = "index.json"
TIMEOUT_SECONDS: Final = 30

type Document = dict[str, object]


class SchemaError(Exception):
    """The schema could not be taken or put back together."""


def split(document: Document) -> dict[str, Document]:
    """Return a schema as files: the index without its definitions, and each definition by its name."""
    definitions = cast("dict[str, Document]", document.get(DEFINITIONS, {}))
    if not definitions:
        msg = f"the schema holds no {DEFINITIONS}"
        raise SchemaError(msg)
    index = {key: value for key, value in document.items() if key != DEFINITIONS}
    return {INDEX: index, **{f"{name}.json": definition for name, definition in definitions.items()}}


def assembled(directory: pathlib.Path) -> Document:
    """Return one version's schema as the specification published it, from its files."""
    index = cast("Document", json.loads((directory / INDEX).read_text(encoding="utf-8")))
    definitions = {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(directory.glob("*.json"))
        if path.name != INDEX
    }
    return {**index, DEFINITIONS: definitions}


def fetched(revision: str, version: str) -> Document:
    """Return one version's schema as the specification's repository holds it at a revision."""
    address = SOURCE.format(revision=revision, version=version)
    with urllib.request.urlopen(address, timeout=TIMEOUT_SECONDS) as answer:
        return cast("Document", json.loads(answer.read()))


def take(root: pathlib.Path, revision: str, fetch: Callable[[str, str], Document] = fetched) -> list[str]:
    """Replace every vendored version with what a revision holds, and record the revision."""
    if not COMMIT.fullmatch(revision):
        msg = f"{revision!r} is not a full commit hash"
        raise SchemaError(msg)
    taken = {version: split(fetch(revision, version)) for version in VERSIONS}
    said: list[str] = []
    for version, files in taken.items():
        directory = root / VENDOR / version
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True)
        for name, content in files.items():
            (directory / name).write_text(
                json.dumps(content, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        said.append(f"vendored the MCP schema {version} at {revision}: {len(files)} files.")
    (root / VENDOR / "REVISION").write_text(f"{revision}\n", encoding="ascii")
    return said


if __name__ == "__main__":
    for line in take(ROOT, sys.argv[2] if sys.argv[1:2] == ["take"] else ""):
        sys.stdout.write(f"{line}\n")
