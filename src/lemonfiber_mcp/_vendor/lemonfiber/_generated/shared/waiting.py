# Copyright (c) 2026 NightWorksIO
"""The shapes `plugins`, `settings` and `status` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Waiting(typing.TypedDict):
    """A service held back until the operator gives what it needs to start."""

    service: str
    """The service."""
    wants: list[Wanted]
    """Everything it waits for."""


type Wanted = WantedSetting | WantedSecret | WantedService
"""One thing a service waits for, never with its value."""


class WantedSecret(typing.TypedDict):
    """A secret nobody has entered."""

    kind: typing.Literal["secret"]
    secret: str
    """The secret, by its name in the secret store."""


class WantedService(typing.TypedDict):
    """The service it runs through, which is held back itself."""

    kind: typing.Literal["service"]
    service: str
    """That service."""


class WantedSetting(typing.TypedDict):
    """A setting only the operator holds, or one holding a value outside its choices."""

    choices: typing.NotRequired[list[str] | None]
    """The values it accepts, where it declares choices."""
    kind: typing.Literal["setting"]
    setting: str
    """The setting."""


__all__ = [
    "Waiting",
    "Wanted",
    "WantedSecret",
    "WantedService",
    "WantedSetting",
]
