# Copyright (c) 2026 NightWorksIO
"""The `plugin-provenance` envelope, and the shapes only `plugin-provenance` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class PluginProvenanceEnvelope(typing.TypedDict):
    """The envelope carrying `plugin-provenance`."""

    api_version: int
    data: Vouched
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["plugin-provenance"]


class Vouch(typing.TypedDict):
    """What one of a plugin's images is vouched for."""

    digest: str
    """The digest that fixes what runs."""
    image: str
    """The registry path, as the manifest declares it."""
    service: str
    """The service the image runs as."""


class Vouched(typing.TypedDict):
    """Every image a plugin pins, and what anybody has said about each."""

    id: str
    """The plugin's id."""
    images: list[Vouch]
    """One answer per image it pins."""
    installable: bool
    """Whether what was found stops an install.

    An unproven image does not: a publisher who signed nothing has made no claim,
    and refusing every unsigned image would refuse most of the registry. A refused
    one does, because a claim that did not hold is worse than none.
    """


__all__ = [
    "PluginProvenanceEnvelope",
    "Vouch",
    "Vouched",
]
