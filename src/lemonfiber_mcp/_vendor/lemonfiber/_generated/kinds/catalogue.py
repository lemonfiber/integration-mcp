# Copyright (c) 2026 NightWorksIO
"""The `catalogue` envelope, and the shapes only `catalogue` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.catalogue__dashboard__lifecycle__status import Criticality


class CatalogueEnvelope(typing.TypedDict):
    """The envelope carrying `catalogue`."""

    api_version: int
    data: CatalogueReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["catalogue"]


class CatalogueReport(typing.TypedDict):
    """What this stack holds, and what it used to."""

    removed: list[RemovedService]
    """The services this stack has dropped, in the order it records them.

    Empty for a stack that has never dropped anything, which is a different thing
    from a stack that keeps no record — and told apart by the fact that a stack
    keeping no record cannot be read as having dropped something it did.
    """
    services: list[CataloguedService]
    """The services, in the order the stack declares them.

    Every service the manifest holds rather than the ones some form would start:
    what a service is *for* is the question being asked, and an answer narrowed to
    what is running would leave the operator unable to ask about the one they are
    deciding whether to run.
    """


class CataloguedService(typing.TypedDict):
    """What one service is for, as the stack declares it."""

    criticality: Criticality
    """How much its absence matters."""
    describes: str
    """What it does for the operator, in plain language."""
    id: str
    """The service's id, which is also its Compose service name."""
    name: str
    """What it is called in front of an operator."""
    without_it: str
    """What going without it costs.

    Carried beside the description rather than left to a separate question,
    because the pair is what turns an inventory into a judgement: knowing that
    Bazarr finds subtitles says nothing about whether its being down matters.
    """


class RemovedService(typing.TypedDict):
    """A service this stack used to carry, and what became of it."""

    id: str
    """The id it was declared under, which is the name an operator will look for."""
    reason: str
    """Why it went."""
    removed_in: str
    """The stack version whose catalogue stopped carrying it."""
    replaced_by: typing.NotRequired[str | None]
    """What took its place, where anything did.

    Absent is an answer and the commonest one: most things that go are not
    replaced, and a record that named the nearest surviving service to avoid an
    empty field would be pointing an operator at something that does not do the
    job they are looking for.
    """


__all__ = [
    "CatalogueEnvelope",
    "CatalogueReport",
    "CataloguedService",
    "RemovedService",
]
