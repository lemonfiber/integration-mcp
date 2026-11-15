# Copyright (c) 2026 NightWorksIO
"""The `setup` envelope, and the shapes only `setup` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.protocols import Protocols


class SetupEnvelope(typing.TypedDict):
    """The envelope carrying `setup`."""

    api_version: int
    data: SetupReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["setup"]


type SetupOutcome = typing.Literal["applied", "abandoned", "already-set-up"]
"""How a setup run ended."""


class SetupReport(typing.TypedDict):
    """What a setup run came to, and what it settled on.

    **Deliberately not the settings themselves.** Setup writes an indexer key and a
    service password among them, and a report a script can read is a report a script
    can log — into a file, a CI transcript, somebody's terminal history. So this says
    what was *decided* and never what was *entered*, and the fields are chosen one at
    a time rather than by serialising a struct that might later gain a secret.

    The indexer's address is left out for that reason rather than because it is
    itself a secret: it is entered beside its key, and the two travel together in
    every place an operator copies them from.
    """

    data_root: typing.NotRequired[str | None]
    """Where the library was put, where a location was chosen."""
    outcome: SetupOutcome
    """How the run ended."""
    protocols: Protocols
    """Which ways of downloading the stack was set up for."""
    service_user: typing.NotRequired[str | None]
    """The user the services run as, as `uid:gid`, where one was set."""


__all__ = [
    "SetupEnvelope",
    "SetupOutcome",
    "SetupReport",
]
