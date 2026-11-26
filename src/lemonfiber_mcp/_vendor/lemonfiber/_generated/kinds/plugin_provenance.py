# Copyright (c) 2026 NightWorksIO
"""The `plugin-provenance` envelope, and the shapes only `plugin-provenance` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Based = BasedRecorded | BasedUnproven | BasedRefused
"""What a service says its image is built on, and what this build makes of it."""


class BasedRecorded(typing.TypedDict):
    """The build of every platform's image is recorded as starting from it."""

    basis: typing.Literal["recorded"]
    digests: list[str]
    """The digest of the upstream image each build is recorded as starting from."""
    image: str
    """The upstream image, as the manifest names it."""
    release: str
    """The upstream's release, as the manifest names it."""


class BasedRefused(typing.TypedDict):
    """The build of some platform's image is not recorded as starting from it."""

    basis: typing.Literal["refused"]
    image: str
    """The upstream image, as the manifest names it."""
    release: str
    """The upstream's release, as the manifest names it."""
    why: str
    """What each such build is recorded as starting from."""


class BasedUnproven(typing.TypedDict):
    """The build provenance could not be asked for."""

    basis: typing.Literal["unproven"]
    image: str
    """The upstream image, as the manifest names it."""
    release: str
    """The upstream's release, as the manifest names it."""
    why: str
    """What stopped it being asked for."""


class PluginProvenanceEnvelope(typing.TypedDict):
    """The envelope carrying `plugin-provenance`."""

    api_version: int
    data: Vouched
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["plugin-provenance"]


type Vouch = VouchSigned | VouchUnproven | VouchRefused
"""What one of a plugin's images is vouched for."""


class VouchRefused(typing.TypedDict):
    """A signature is offered and it does not hold."""

    built_on: typing.NotRequired[Based | None]
    """What the service says its image is built on, and what its build provenance makes
    of that, where it says.
    """
    digest: str
    """The digest that fixes what runs."""
    image: str
    """The registry path, as the manifest declares it."""
    provenance: typing.Literal["refused"]
    service: str
    """The service the image runs as."""
    why: str
    """Every way it does not."""


class VouchSigned(typing.TypedDict):
    """A signature over a payload naming this digest verified against a held key."""

    built_on: typing.NotRequired[Based | None]
    """What the service says its image is built on, and what its build provenance makes
    of that, where it says.
    """
    by: str
    """Which key it verified against, so the answer names what was trusted."""
    digest: str
    """The digest that fixes what runs."""
    image: str
    """The registry path, as the manifest declares it."""
    provenance: typing.Literal["signed"]
    service: str
    """The service the image runs as."""


class VouchUnproven(typing.TypedDict):
    """Nothing was established, and nothing follows from it either way."""

    built_on: typing.NotRequired[Based | None]
    """What the service says its image is built on, and what its build provenance makes
    of that, where it says.
    """
    digest: str
    """The digest that fixes what runs."""
    image: str
    """The registry path, as the manifest declares it."""
    provenance: typing.Literal["unproven"]
    service: str
    """The service the image runs as."""
    why: str
    """What stopped it being established."""


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
    one does, because a claim that did not hold is worse than none, and so does an
    upstream image a service says it is built on that its build provenance does not
    record.
    """


__all__ = [
    "Based",
    "BasedRecorded",
    "BasedRefused",
    "BasedUnproven",
    "PluginProvenanceEnvelope",
    "Vouch",
    "VouchRefused",
    "VouchSigned",
    "VouchUnproven",
    "Vouched",
]
