# Copyright (c) 2026 NightWorksIO
"""What the generator writes each tool as: the request it reaches, its input, and what the protocol is told of it."""

import enum
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


class Reach(enum.StrEnum):
    """How a tool reaches the stack, each through its own call of the client."""

    READ = "read"
    """A read answering with one envelope, asked by its name."""
    LOGS = "logs"
    """What the services have been saying, a line at a time, asked without following."""
    FILE = "file"
    """A read answering with a file rather than an envelope."""
    REHEARSAL = "rehearsal"
    """An action asked to say what it would do and write nothing."""
    ACTION = "action"
    """An action carried out."""


@dataclass(frozen=True, slots=True)
class ToolShape:
    """One tool as the contract describes it; its words are written elsewhere."""

    name: str
    """What the tool is called by, unique among the tools."""
    reach: Reach
    target: str
    """The read's name, or the action's, as the client asks for it."""
    capability: str
    """The path the stack's capabilities name this request by."""
    parameters: tuple[str, ...]
    """The name of every parameter the tool takes, as the request carries it."""
    input_schema: Mapping[str, object]
    """The JSON Schema of what the tool takes."""
    resource: str | None
    """The resource's address, or its template where it takes parameters; None for a write."""
    read_only: bool
    destructive: bool
    idempotent: bool
