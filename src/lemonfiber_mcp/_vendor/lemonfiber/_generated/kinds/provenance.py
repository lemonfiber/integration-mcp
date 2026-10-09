# Copyright (c) 2026 NightWorksIO
"""The `provenance` envelope, and the shapes only `provenance` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class ProvenanceEnvelope(typing.TypedDict):
    """The envelope carrying `provenance`."""

    api_version: int
    data: ProvenanceReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["provenance"]


class ProvenanceReport(typing.TypedDict):
    """Where every service in this stack comes from."""

    services: list[ServiceProvenance]
    """The services, in the order the stack declares them.

    Every service the manifest holds rather than the ones some form would start:
    what is *in* this stack is the question being asked, and an answer narrowed to
    what is running would leave the operator unable to ask about the service they
    are deciding whether to run.
    """


class ServiceProvenance(typing.TypedDict):
    """Where one service comes from, as the stack declares it."""

    digest: typing.NotRequired[str | None]
    """The digest of the image that runs, where the stack names one.

    Beside the tag rather than instead of it: the tag is the version somebody reads,
    and the digest is the one image that version was when it was pinned, which is
    what is pulled and what somebody verifies against the registry.
    """
    id: str
    """The service's id, which is also its Compose service name."""
    image: str
    """The image it runs, without a tag."""
    license: str
    """The SPDX identifier of the licence it is published under.

    Stated rather than summarised as *open source*, because the identifier is what
    somebody checks against the project — and because the four in this stack are
    not interchangeable to anybody deciding what to do with what they run.
    """
    name: str
    """What it is called in front of an operator."""
    pinned: str
    """The exact tag this stack pins it at.

    Kept apart from the image rather than written as one reference, so that a
    caller comparing what is pinned against what a project has released is
    comparing versions rather than parsing them out of a string. The two are
    printed together for a person, because a version without the image it belongs
    to names nothing that can be fetched.
    """
    upstream: str
    """The project it is built from.

    The whole point of the entry for anybody verifying: the licence is a string
    this stack wrote down, and this is where somebody goes to find out whether the
    project still agrees with it.
    """


__all__ = [
    "ProvenanceEnvelope",
    "ProvenanceReport",
    "ServiceProvenance",
]
