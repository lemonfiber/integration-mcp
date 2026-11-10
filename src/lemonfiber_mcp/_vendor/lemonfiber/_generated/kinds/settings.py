# Copyright (c) 2026 NightWorksIO
"""The `settings` envelope, and the shapes only `settings` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.lifecycle__plugins__reset__settings__substitution__update import StackMoveTaken
from ..shared.lifecycle__plugins__settings__substitution__update import Unvetted
from ..shared.plugins__settings__status import Waiting
from ..shared.settings__wizard import Choosable


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
    met: bool
    """Whether those settings hold what it needs now."""
    needs: dict[str, list[str]]
    """The values of other settings under which the variable is written: each setting
    with the values it has to hold one of.
    """
    service: str
    """The service."""
    variable: str
    """The variable it is read into."""


type SecretFrom = typing.Literal["operator", "recipe", "granted", "minted"]
"""Where a secret's value came from."""


class SettingChange(typing.TypedDict):
    """A change to one or more settings, made in one act."""

    agreement: str
    """What this reading names itself, part by part."""
    applied: bool
    """Whether it was written."""
    regenerates: list[str]
    """Every service whose entry the change regenerates."""
    restarts: list[str]
    """Every running service the change restarts."""
    settings: list[SettingMove]
    """Each setting the act moves, in name order."""
    starts: list[str]
    """Every service held back that the change starts, having given the last thing it
    waited for.
    """
    unrestarted: typing.NotRequired[str | None]
    """Why the services it restarts were not restarted, where they were not."""
    waiting: list[Waiting]
    """The services held back once the change is made, each with what it waits for."""


class SettingMove(typing.TypedDict):
    """One setting a change moves."""

    consequence: typing.NotRequired[str | None]
    """What moving it costs, where it costs anything."""
    setting: str
    """The setting."""
    value: typing.NotRequired[str | None]
    """What it is to hold, or nothing where it is cleared."""
    was: typing.NotRequired[str | None]
    """What it holds now."""


class SettingRead(typing.TypedDict):
    """One setting."""

    choices: typing.NotRequired[list[Choosable] | None]
    """Every value it accepts, where its manifest declares them."""
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
    guards: typing.NotRequired[list[StackMoveTaken]]
    """Each of lemonfiber's own guards this act moved onto its plugin after its own
    change, or on a reading would move, for good and with no yes of its own; one it
    could not move stays on offer and says why.
    """
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
    waiting: list[Waiting]
    """The services held back until the operator gives what they need to start, each
    with what it waits for, as status names them.
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
    "SettingMove",
    "SettingRead",
    "SettingsEnvelope",
    "SettingsReport",
]
