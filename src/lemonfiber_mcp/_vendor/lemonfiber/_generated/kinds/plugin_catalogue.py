# Copyright (c) 2026 NightWorksIO
"""The `plugin-catalogue` envelope, and the shapes only `plugin-catalogue` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.instant import Instant


class CatalogueFailure(typing.TypedDict):
    """Why the catalogue's index was not read."""

    code: str
    """The problem code an install by name would be refused with."""
    summary: str
    """What went wrong, in one line."""


class CataloguedPlugin(typing.TypedDict):
    """One plugin the catalogue offers."""

    description: str
    """What it does, in its author's words."""
    id: str
    """The plugin's id, which is the name it is installed by."""
    installed: typing.NotRequired[InstalledVersion | None]
    """The version installed on this machine. Absent where it is not installed."""
    name: str
    """What it calls itself."""
    version: str
    """The version the catalogue reviewed."""
    without_it: str
    """What the household is without it."""


class InstalledVersion(typing.TypedDict):
    """The version of a catalogued plugin installed here, against the catalogue's."""

    newer: bool
    """Whether the catalogue's version is above it by semver."""
    version: str
    """The version installed."""


class PluginCatalogueEnvelope(typing.TypedDict):
    """The envelope carrying `plugin-catalogue`."""

    api_version: int
    data: PluginCatalogueReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["plugin-catalogue"]


class PluginCatalogueReport(typing.TypedDict):
    """What the catalogue offers, or why it was not read."""

    entries: list[CataloguedPlugin]
    """Every plugin the verified index offers, by id; empty where it was not read."""
    failure: typing.NotRequired[CatalogueFailure | None]
    """Why the index could not be read. Present where it failed."""
    published: typing.NotRequired[Instant | None]
    """When the index listed was published. Present where it was read."""
    serial: typing.NotRequired[int | None]
    """Which release of the catalogue the index listed is. Present where it was read."""
    setting: typing.NotRequired[ReachSetting | None]
    """The setting that keeps the catalogue from being asked, and how to let it be.
    Present where it is switched off.
    """
    state: PluginCatalogueState
    """Whether the catalogue was read, switched off, or could not be read."""
    unreadable: typing.NotRequired[int | None]
    """How many entries the index holds that could not be listed, for lacking a fact an
    entry carries. Present where it was read.
    """


type PluginCatalogueState = typing.Literal["listed", "off", "failed"]
"""Whether the catalogue was read."""


class ReachSetting(typing.TypedDict):
    """A setting that keeps a request from being made, and the change that lets it be."""

    action: SettingWrite
    """The action that writes it."""
    key: str
    """The setting."""
    value: str
    """The value that lets the request be made."""


type SettingWrite = typing.Literal["config-set"]
"""The action a setting is written with."""


__all__ = [
    "CatalogueFailure",
    "CataloguedPlugin",
    "InstalledVersion",
    "PluginCatalogueEnvelope",
    "PluginCatalogueReport",
    "PluginCatalogueState",
    "ReachSetting",
    "SettingWrite",
]
