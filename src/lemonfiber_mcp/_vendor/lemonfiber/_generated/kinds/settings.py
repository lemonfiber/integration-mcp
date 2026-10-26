# Copyright (c) 2026 NightWorksIO
"""The `settings` envelope, and the shapes only `settings` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.lifecycle__plugins__settings__substitution__update import Unvetted


type Owner = OwnerCore | OwnerNamespace
"""Whose a setting or a secret is."""


class OwnerCore(typing.TypedDict):
    """The core's."""

    of: typing.Literal["core"]


class OwnerNamespace(typing.TypedDict):
    """A plugin's, or a stack service's, by its namespace."""

    namespace: str
    """The namespace."""
    of: typing.Literal["namespace"]


class Reader(typing.TypedDict):
    """One service reading a setting or a secret."""

    default: typing.NotRequired[str | None]
    """What the service's manifest declares while no value is recorded."""
    service: str
    """The service."""
    variable: str
    """The variable it is read into."""


type SecretFrom = typing.Literal["operator", "recipe", "granted", "minted"]
"""Where a secret's value came from."""


class SettingChange(typing.TypedDict):
    """A change to one setting."""

    agreement: str
    """What this reading names itself, part by part."""
    applied: bool
    """Whether it was written."""
    consequence: typing.NotRequired[str | None]
    """What the change costs, where it costs anything."""
    regenerates: list[str]
    """Every service whose entry the change regenerates."""
    restarts: list[str]
    """Every running service the change restarts."""
    setting: str
    """The setting."""
    unrestarted: typing.NotRequired[str | None]
    """Why the services it restarts were not restarted, where they were not."""
    value: typing.NotRequired[str | None]
    """What it is to hold, or nothing where it is cleared."""
    was: typing.NotRequired[str | None]
    """What it holds now."""


class SettingRead(typing.TypedDict):
    """One setting."""

    environment: typing.NotRequired[str | None]
    """The environment file's key it is held under, where it is held there."""
    name: str
    """Its name."""
    readers: list[Reader]
    """Each service that reads it."""
    value: typing.NotRequired[str | None]
    """The operator's value, where one is recorded."""
    whose: Owner
    """Whose it is."""


class SettingsEnvelope(typing.TypedDict):
    """The envelope carrying `settings`."""

    api_version: int
    data: SettingsReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["settings"]


class SettingsReport(typing.TypedDict):
    """Every setting and secret the stack's services read, and what changing a setting came to."""

    change: typing.NotRequired[SettingChange | None]
    """The change asked for, where one was."""
    rehearsed: bool
    """Whether this was a rehearsal."""
    secrets: list[SecretRead]
    """Every secret a service's environment names, in name order, never with its value."""
    settings: list[SettingRead]
    """Every setting, in name order."""
    unvetted: typing.NotRequired[Unvetted | None]
    """The operator's overlay and every service it changes, where there is one: merged
    over the project this run would start, and held to nothing lemonfiber vets.
    """


SecretRead = typing.TypedDict(
    "SecretRead",
    {
        "from": typing.NotRequired[SecretFrom | None],
        "held": bool,
        "name": str,
        "readers": list[Reader],
        "whose": Owner,
    },
)
"""One secret, without its value."""


__all__ = [
    "Owner",
    "OwnerCore",
    "OwnerNamespace",
    "Reader",
    "SecretFrom",
    "SecretRead",
    "SettingChange",
    "SettingRead",
    "SettingsEnvelope",
    "SettingsReport",
]
