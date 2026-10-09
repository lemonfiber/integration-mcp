# Copyright (c) 2026 NightWorksIO
"""Every tool, resource and answer the server writes holds to the MCP specification's own schema."""

import datetime
import pathlib
import types as builtin_types
from typing import TYPE_CHECKING, Any, Final

import jsonschema
import pytest
from lemonfiber import CapabilitySet

from lemonfiber_mcp import catalogue, outcome
from lemonfiber_mcp._generated.tools import TOOLS
from lemonfiber_mcp.catalogue import Audience
from lemonfiber_mcp.withheld import Withholding
from scripts import vendor_mcp_schema

if TYPE_CHECKING:
    from collections.abc import Callable

    import mcp_types as types
    from lemonfiber._generated import CapabilityState
    from pydantic import BaseModel

ROOT: Final = pathlib.Path(__file__).resolve().parent.parent
SCHEMAS: Final = sorted(path for path in (ROOT / vendor_mcp_schema.VENDOR).iterdir() if path.is_dir())
"""Each version of the specification's schema, vendored at the revision `vendor/mcp-schema/REVISION` names."""


def validator(path: pathlib.Path, definition: str) -> Callable[[dict[str, Any]], None]:
    """Return a check of one definition of a version of the specification's schema, raising where it does not hold."""
    schema = {**vendor_mcp_schema.assembled(path), "$ref": f"#/$defs/{definition}"}
    checker = jsonschema.Draft202012Validator(schema)

    def holds(instance: dict[str, Any]) -> None:
        assert [error.message for error in checker.iter_errors(instance)] == []

    return holds


def wire(model: BaseModel) -> dict[str, Any]:
    """Return a protocol object as it is written on the wire."""
    return model.model_dump(by_alias=True, mode="json", exclude_none=True)


def everything_offered(audience: Audience) -> dict[str, types.Tool]:
    """Return every tool an audience could be offered, with every capability available."""
    states: dict[str, CapabilityState] = {shape.capability: "available" for shape in TOOLS}
    held = CapabilitySet(
        builtin_types.MappingProxyType(states),
        datetime.datetime.now(datetime.UTC),
        "operator",
    )
    return {**catalogue.offered(held, audience), **catalogue.connection_only(audience)}


def test_the_schema_is_vendored_for_each_version() -> None:
    assert [path.name for path in SCHEMAS] == list(vendor_mcp_schema.VERSIONS)


@pytest.mark.parametrize("schema", SCHEMAS, ids=lambda path: path.name)
@pytest.mark.parametrize("audience", list(Audience))
def test_every_tool_holds_to_the_specification(schema: pathlib.Path, audience: Audience) -> None:
    holds = validator(schema, "Tool")
    for tool in everything_offered(audience).values():
        holds(wire(tool))
        jsonschema.Draft202012Validator.check_schema(tool.input_schema)


@pytest.mark.parametrize("schema", SCHEMAS, ids=lambda path: path.name)
def test_every_resource_and_template_holds_to_the_specification(schema: pathlib.Path) -> None:
    resource, template = validator(schema, "Resource"), validator(schema, "ResourceTemplate")
    for name, tool in everything_offered(Audience.OPERATOR).items():
        address = catalogue.SHAPES[name].resource
        if address is None:
            continue
        written = {"name": name, "description": tool.description, "mimeType": "application/json"}
        if "{" in address:
            template({**written, "uriTemplate": address})
        else:
            resource({**written, "uri": address})


@pytest.mark.parametrize("schema", SCHEMAS, ids=lambda path: path.name)
def test_an_answer_and_a_failure_hold_to_the_specification(schema: pathlib.Path) -> None:
    holds = validator(schema, "CallToolResult")
    withholding = Withholding()
    holds(wire(outcome.answered({"api_version": 1, "kind": "status", "data": {}}, withholding)))
    failure = outcome.Failure(outcome.MISASKED, refusal={"code": "READ-4", "sentence": "Name something."})
    holds(wire(outcome.failed(failure, withholding)))
