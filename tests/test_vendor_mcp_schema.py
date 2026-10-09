# Copyright (c) 2026 NightWorksIO
"""Vendoring the MCP specification's schema a definition a file, and putting it back together."""

import io
import json
from typing import TYPE_CHECKING, Final

import pytest

from scripts import vendor_mcp_schema

if TYPE_CHECKING:
    import pathlib

REVISION: Final = "c" * 40
SCHEMA: Final = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$defs": {
        "Tool": {"type": "object", "properties": {"name": {"$ref": "#/$defs/Name"}}},
        "Name": {"type": "string"},
    },
}


def fetch(revision: str, version: str) -> vendor_mcp_schema.Document:
    """Stand in for the specification's repository, answering the same schema for every version."""
    assert revision == REVISION
    assert version in vendor_mcp_schema.VERSIONS
    return json.loads(json.dumps(SCHEMA))


def test_a_revision_is_taken_a_definition_a_file_and_assembles_back(tmp_path: pathlib.Path) -> None:
    said = vendor_mcp_schema.take(tmp_path, REVISION, fetch)
    assert len(said) == len(vendor_mcp_schema.VERSIONS)
    for version in vendor_mcp_schema.VERSIONS:
        directory = tmp_path / vendor_mcp_schema.VENDOR / version
        assert sorted(path.name for path in directory.iterdir()) == ["Name.json", "Tool.json", "index.json"]
        assert vendor_mcp_schema.assembled(directory) == SCHEMA
    assert (tmp_path / vendor_mcp_schema.VENDOR / "REVISION").read_text(encoding="ascii") == f"{REVISION}\n"


def test_taking_again_replaces_what_was_there(tmp_path: pathlib.Path) -> None:
    vendor_mcp_schema.take(tmp_path, REVISION, fetch)
    stale = tmp_path / vendor_mcp_schema.VENDOR / vendor_mcp_schema.VERSIONS[0] / "Gone.json"
    stale.write_text("{}", encoding="utf-8")
    vendor_mcp_schema.take(tmp_path, REVISION, fetch)
    assert not stale.exists()


def test_what_is_not_a_full_commit_is_refused(tmp_path: pathlib.Path) -> None:
    with pytest.raises(vendor_mcp_schema.SchemaError, match="not a full commit hash"):
        vendor_mcp_schema.take(tmp_path, "main", fetch)


def test_a_schema_with_no_definitions_is_refused() -> None:
    with pytest.raises(vendor_mcp_schema.SchemaError, match="holds no"):
        vendor_mcp_schema.split({"$schema": "x"})


def test_a_schema_is_fetched_from_the_pinned_revision(monkeypatch: pytest.MonkeyPatch) -> None:
    asked: list[str] = []

    def answer(address: str, timeout: float) -> io.BytesIO:
        asked.append(address)
        assert timeout == vendor_mcp_schema.TIMEOUT_SECONDS
        return io.BytesIO(json.dumps(SCHEMA).encode())

    monkeypatch.setattr(vendor_mcp_schema.urllib.request, "urlopen", answer)
    assert vendor_mcp_schema.fetched(REVISION, "2025-11-25") == SCHEMA
    assert asked == [
        f"https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/{REVISION}/schema/2025-11-25/schema.json",
    ]


def test_the_vendored_copy_names_a_full_revision() -> None:
    written = (
        (vendor_mcp_schema.ROOT / vendor_mcp_schema.VENDOR / "REVISION").read_text(encoding="ascii").strip()
    )
    assert vendor_mcp_schema.COMMIT.fullmatch(written)
