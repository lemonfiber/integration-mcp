# Copyright (c) 2026 NightWorksIO
"""The tools one credential is offered: the generated shapes, the written words, and what the stack admits.

A tool is offered where the stack's capabilities say the credential may use
the request it reaches, or that a setting must be turned on first. Its words
are the operator's, or the household's for a member, and a member is offered a
tool only where it has household words, with only the parameters those words
describe. Whose credential it is the capabilities say by its scope; until they
have said, it is described as a member's, so a member never reads a technical
word.
"""

import enum
import functools
import importlib.resources
import re
import tomllib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, cast

import mcp_types as types

from lemonfiber_mcp._generated.tools import TOOLS
from lemonfiber_mcp.shapes import Reach, ToolShape

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from lemonfiber import CapabilitySet
    from lemonfiber._generated import CredentialScope

OFFERED_STATES: Final = frozenset({"available", "unconfigured"})
"""What a capability may come to for its tool to be offered."""
UNCONFIGURED: Final = "unconfigured"
UNCONFIGURED_NOTE: Final = " A setting on the stack has to be turned on before this answers."
CONNECTION: Final = "connection"
JOB: Final = "job"
WORDS: Final = "descriptions.toml"


class Audience(enum.StrEnum):
    """Whose words a tool is described in."""

    OPERATOR = "operator"
    HOUSEHOLD = "household"


MEMBER: Final = "member"
"""The scope of a household member's credential, which is offered the household's words."""
UNKNOWN: Final = Audience.HOUSEHOLD
"""Whose words a credential is described in before the stack has said its scope."""


def audience_of(scope: CredentialScope) -> Audience:
    """Return whose words a credential of a scope is described in: the household's for a member's."""
    return Audience.HOUSEHOLD if scope == MEMBER else Audience.OPERATOR


@dataclass(frozen=True, slots=True)
class Words:
    """What is written of one tool."""

    operator: str
    parameters: Mapping[str, str]
    household: str | None
    household_parameters: Mapping[str, str]


WRITTEN: Final[tuple[ToolShape, ...]] = (
    ToolShape(
        name=CONNECTION,
        reach=Reach.READ,
        target=CONNECTION,
        capability="",
        parameters=(),
        input_schema={"type": "object", "properties": {}, "additionalProperties": False},
        resource=None,
        read_only=True,
        destructive=False,
        idempotent=True,
    ),
    ToolShape(
        name=JOB,
        reach=Reach.READ,
        target=JOB,
        capability="",
        parameters=(JOB,),
        input_schema={
            "type": "object",
            "properties": {JOB: {"type": "string"}},
            "required": [JOB],
            "additionalProperties": False,
        },
        resource=None,
        read_only=True,
        destructive=False,
        idempotent=True,
    ),
)
"""The two tools the contract does not generate: where the server stands, and where started work stands."""

SHAPES: Final[Mapping[str, ToolShape]] = {shape.name: shape for shape in (*TOOLS, *WRITTEN)}
"""Every tool the server knows, generated and written, by name."""

SCHEME: Final = "lemonfiber"
"""The scheme every resource address the server offers is written in."""


def address_pattern(resource: str) -> re.Pattern[str]:
    """Return what a resource template's address matches, below its scheme: each segment it fills one segment."""
    fixed = resource.removeprefix(f"{SCHEME}://").split("{?", 1)[0]
    return re.compile(
        "".join(
            f"(?P<{part[1:-1]}>[^/]+)" if part.startswith("{") else re.escape(part)
            for part in re.split(r"(\{[a-z_]+\})", fixed)
        ),
    )


ADDRESSED: Final[tuple[tuple[re.Pattern[str], ToolShape], ...]] = tuple(
    (address_pattern(shape.resource), shape) for shape in TOOLS if shape.resource is not None
)
"""Every read a resource address names, by what its address matches below the scheme."""


def strings(value: object) -> dict[str, str]:
    """Return a TOML table of strings as a mapping, refusing anything else."""
    if not isinstance(value, dict):
        msg = "a parameters table is not a table"
        raise TypeError(msg)
    table = cast("dict[str, object]", value)
    if not all(isinstance(text, str) for text in table.values()):
        msg = "a parameter's description is not text"
        raise TypeError(msg)
    return cast("dict[str, str]", table)


def read_words(text: str) -> dict[str, Words]:
    """Return the words written for each tool, as `descriptions.toml` writes them."""
    written: dict[str, Words] = {}
    for name, entry in tomllib.loads(text).items():
        table = cast("dict[str, object]", entry)
        household = cast("dict[str, object]", table.get("household", {}))
        described = household.get("description")
        written[name] = Words(
            operator=str(table["operator"]),
            parameters=strings(table.get("parameters", {})),
            household=None if described is None else str(described),
            household_parameters=strings(household.get("parameters", {})),
        )
    return written


@functools.cache
def words() -> Mapping[str, Words]:
    """Return the words written for each tool, read once from the package."""
    return read_words(importlib.resources.files(__package__).joinpath(WORDS).read_text(encoding="utf-8"))


def described_schema(
    shape: ToolShape,
    described: Mapping[str, str],
    offered: Iterable[str],
) -> dict[str, object]:
    """Return a tool's input schema holding only the offered parameters, each described.

    A parameter's description is the written one where there is one, and the
    contract's otherwise; one with neither is left undescribed.
    """
    schema = dict(shape.input_schema)
    properties = cast("dict[str, dict[str, object]]", schema.get("properties", {}))
    kept = [name for name in shape.parameters if name in set(offered)]
    schema["properties"] = {
        name: properties[name]
        if name not in described
        else {**properties[name], "description": described[name]}
        for name in kept
    }
    if "required" in schema:
        schema["required"] = [name for name in cast("list[str]", schema["required"]) if name in kept]
    return schema


def tool(shape: ToolShape, audience: Audience, state: str | None = None) -> types.Tool | None:
    """Return a tool as one audience is offered it, or None where that audience is offered none."""
    written = words()[shape.name]
    offered: Iterable[str]
    if audience is Audience.OPERATOR:
        description, described = written.operator, written.parameters
        offered = shape.parameters
    elif written.household is not None:
        description, described = written.household, written.household_parameters
        offered = described
    else:
        return None
    if state == UNCONFIGURED:
        description += UNCONFIGURED_NOTE
    return types.Tool(
        name=shape.name,
        description=description,
        input_schema=described_schema(shape, described, offered),
        annotations=types.ToolAnnotations(
            read_only_hint=shape.read_only,
            destructive_hint=shape.destructive,
            idempotent_hint=shape.idempotent,
            open_world_hint=False,
        ),
    )


def offered(capabilities: CapabilitySet, audience: Audience) -> dict[str, types.Tool]:
    """Return every tool a credential is offered, by name, given what the stack says it may do.

    `job` is offered with any action the credential may call, since only an
    action starts work it would redeem; no member is offered an action.
    """
    tools: dict[str, types.Tool] = {}
    for shape in TOOLS:
        state = capabilities.of(shape.capability)
        if state not in OFFERED_STATES:
            continue
        made = tool(shape, audience, state)
        if made is None:
            continue
        tools[shape.name] = made
        if shape.reach is Reach.ACTION:
            tools[JOB] = cast("types.Tool", tool(SHAPES[JOB], audience))
    return tools


def connection_only(audience: Audience) -> dict[str, types.Tool]:
    """Return the one tool offered before the stack has said what this credential may do.

    Every audience has words for it, which the suite holds to.
    """
    return {CONNECTION: cast("types.Tool", tool(SHAPES[CONNECTION], audience))}
