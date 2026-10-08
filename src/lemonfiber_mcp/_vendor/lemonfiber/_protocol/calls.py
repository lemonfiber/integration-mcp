# Copyright (c) 2026 NightWorksIO
"""What a request carries, and the answer a transport hands back."""

import json
import urllib.parse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from http import HTTPMethod
from typing import TYPE_CHECKING, Final

from lemonfiber.reads import ACTIONS, BUNDLE, CAPABILITIES, JOBS, LOGS, SESSION

if TYPE_CHECKING:
    from lemonfiber.credential import Credential
    from lemonfiber.reads import Read

type Scalar = str | int | bool
"""One value a query parameter carries."""

type Query = Mapping[str, Scalar | Sequence[Scalar] | None]
"""A read's parameters. A list is the parameter once per value; `None` or an empty list sends nothing."""

type Json = bool | int | float | str | Sequence[Json] | Mapping[str, Json] | None
"""A value an action's arguments may carry."""

NOTHING_SAFE: Final = ""
"""The characters a path segment leaves unquoted beyond the unreserved ones: none."""

JSON_TYPE: Final = "application/json"
"""What every request but the one for a file asks to be answered in, and what a body is sent as."""

ANY_TYPE: Final = "*/*"
"""What a request for a file takes, whatever it is served as."""

DEFAULT_TIMEOUT: Final = 30.0
"""How many seconds a call waits for its answer, unless the client is told otherwise."""


@dataclass(frozen=True, slots=True)
class Call:
    """One request, as every transport sends it.

    Its headers carry the credential and its body may carry a password, so
    neither is shown when the call is printed.
    """

    method: HTTPMethod
    path: str
    headers: Mapping[str, str] = field(default_factory=dict[str, str], repr=False)
    body: bytes | None = field(default=None, repr=False)


@dataclass(frozen=True, slots=True)
class Answer:
    """One answer, as every transport hands it back: header names lower-cased."""

    status: int
    headers: Mapping[str, str]
    body: bytes


def received(status: int, headers: Mapping[str, str], body: bytes) -> Answer:
    """Return an answer as a transport received it, its header names lower-cased."""
    return Answer(status, {name.lower(): value for name, value in headers.items()}, body)


def segment(name: str) -> str:
    """Write a name as one path segment, so a separator in it reaches lemonfiber as written."""
    return urllib.parse.quote(name, safe=NOTHING_SAFE)


def search(query: Query | None) -> str:
    """Return a query string, or nothing where there is nothing to ask for. The credential is never in it."""
    pairs: list[tuple[str, str]] = []
    for key, value in (query or {}).items():
        pairs.extend((key, written(one)) for one in listed(value))
    return f"?{urllib.parse.urlencode(pairs)}" if pairs else ""


def listed(value: Scalar | Sequence[Scalar] | None) -> list[Scalar]:
    """Return a query value as the values it sends: none for nothing, one for a scalar, each of a list."""
    if value is None:
        return []
    if isinstance(value, str | int):
        return [value]
    return list(value)


def written(value: Scalar) -> str:
    """Write one query value as lemonfiber reads it."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def with_credential(call: Call, credential: Credential) -> Call:
    """Return the call carrying the credential in its header."""
    return Call(call.method, call.path, {**call.headers, **credential.header()}, call.body)


def read_call(read: Read, query: Query | None) -> Call:
    """Ask for what a command prints under `--json`."""
    return Call(HTTPMethod.GET, read.path + search(query), {"Accept": JSON_TYPE})


def capabilities_call() -> Call:
    """Ask what the stack can do, for the credential the call carries."""
    return Call(HTTPMethod.GET, CAPABILITIES, {"Accept": JSON_TYPE})


def logs_call(services: Sequence[str], forms: Sequence[str], tail: int | None) -> Call:
    """Ask for what the services have been saying: those named, of the forms named, the last `tail` lines.

    Following the logs as they grow is not asked for here: lemonfiber answers it
    with a job rather than with lines, and the lines arrive on the live stream.
    """
    query: Query = {"service": services, "form": forms, "tail": tail}
    return Call(HTTPMethod.GET, LOGS + search(query), {"Accept": JSON_TYPE})


def bundle_call(name: str) -> Call:
    """Ask for one support bundle, by the name it was written under."""
    return Call(HTTPMethod.GET, f"{BUNDLE}/{segment(name)}", {"Accept": ANY_TYPE})


def action_call(name: str, arguments: Mapping[str, Json] | None) -> Call:
    """Tell lemonfiber to do something the command line could also do."""
    body = json.dumps(dict(arguments or {})).encode()
    headers = {"Accept": JSON_TYPE, "Content-Type": JSON_TYPE}
    return Call(HTTPMethod.POST, f"{ACTIONS}/{segment(name)}", headers, body)


def job_call(job: str, method: HTTPMethod) -> Call:
    """Ask where work stands with `GET`, or let its name go with `DELETE`."""
    return Call(method, f"{JOBS}/{segment(job)}", {"Accept": JSON_TYPE})


def session_call(password: str, name: str | None) -> Call:
    """Offer a password, and a household member's name where it is one, for a session."""
    offer = {"password": password} if name is None else {"name": name, "password": password}
    headers = {"Accept": JSON_TYPE, "Content-Type": JSON_TYPE}
    return Call(HTTPMethod.POST, SESSION, headers, json.dumps(offer).encode())
