# Copyright (c) 2026 NightWorksIO
"""Each request a client can make, paired with the reading of its answer."""

from dataclasses import dataclass
from http import HTTPMethod
from typing import TYPE_CHECKING

from lemonfiber._protocol.answers import (
    bundle_of,
    capabilities_of,
    envelope_of,
    log_lines_of,
    picture_of,
    session_of,
    standing_of,
)
from lemonfiber._protocol.calls import (
    Answer,
    Call,
    action_call,
    bundle_call,
    capabilities_call,
    job_call,
    logs_call,
    picture_call,
    read_call,
    session_call,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from lemonfiber._generated import Envelope, LogEnvelope
    from lemonfiber._protocol.calls import Json, Query
    from lemonfiber.capabilities import CapabilitySet
    from lemonfiber.credential import Session
    from lemonfiber.files import BundleFile, Picture
    from lemonfiber.jobs import JobStanding
    from lemonfiber.reads import Read


@dataclass(frozen=True, slots=True)
class Operation[T]:
    """One request, and what its answer comes to: a client sends `call` and hands what came back to `read`."""

    call: Call
    read: Callable[[Answer], T]
    again: bool = False
    """Whether the request is a read, which may be asked again after a passing failure."""


def reading(read: Read, query: Query | None) -> Operation[Envelope]:
    """Ask for what a command prints under `--json`."""
    return Operation(read_call(read, query), envelope_of, again=True)


def capabilities() -> Operation[CapabilitySet]:
    """Ask what the stack can do, for the credential the call carries."""
    return Operation(capabilities_call(), capabilities_of, again=True)


def logs(services: Sequence[str], forms: Sequence[str], tail: int | None) -> Operation[list[LogEnvelope]]:
    """Ask for what the services have been saying, a `log` envelope a line."""
    return Operation(logs_call(services, forms, tail), log_lines_of, again=True)


def bundle(name: str) -> Operation[BundleFile]:
    """Fetch one support bundle, by name, as the bytes it is."""
    return Operation(bundle_call(name), lambda answer: bundle_of(name, answer), again=True)


def picture(template: str, title: str, query: Query | None) -> Operation[Picture]:
    """Fetch one of a title's pictures, as the raster image it is."""
    return Operation(picture_call(template, title, query), picture_of, again=True)


def action(name: str, arguments: Mapping[str, Json] | None) -> Operation[Envelope]:
    """Tell lemonfiber to do something the command line could also do."""
    return Operation(action_call(name, arguments), envelope_of)


def job(name: str) -> Operation[JobStanding]:
    """Ask where the work a name stands for got to."""
    return Operation(job_call(name, HTTPMethod.GET), lambda answer: standing_of(name, answer), again=True)


def release(name: str) -> Operation[JobStanding]:
    """Let a name go, ending the work it stands for, and say where it now stands."""
    return Operation(job_call(name, HTTPMethod.DELETE), lambda answer: standing_of(name, answer))


def admission(password: str, name: str | None) -> Operation[Session]:
    """Offer a password, and a household member's name where it is one, for a session."""
    return Operation(session_call(password, name), session_of)
