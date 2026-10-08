# Copyright (c) 2026 NightWorksIO
"""The shapes `dashboard`, `lifecycle` and `status` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .catalogue__dashboard__lifecycle__status import Criticality


class Service(typing.TypedDict):
    """One service, as it stands."""

    criticality: Criticality
    """How much its absence costs, so a summary can weigh it."""
    depends_on: list[str]
    """The services it needs before it can work, as the manifest declares them.
    Carried so a failure can be attributed to the thing underneath it rather
    than counted as one more independent thing wrong.
    """
    describes: str
    """What it does for the operator, in the stack's own words.

    Carried on the service rather than looked up where it is shown, because this
    is the one struct every surface reads: a listing, the machine-readable reply,
    the web API and the terminal's panel all render this, and a description
    fetched separately by each of them would be four chances to render three.

    The stack's words rather than lemonfiber's, for the reason its absence cost is:
    a stack that adds a service should not need a lemonfiber release before it can
    say what that service is for.
    """
    exit: typing.NotRequired[int | None]
    """How it exited, where it has exited."""
    forms: list[str]
    """Every form it is running for, in the order the stack declares them.

    All of them rather than one, because a service two forms share is there for
    both, and stopping one of them leaves it running for the other. Empty where no
    form it belongs to is up: a service nobody's form holds is not missing from one.
    """
    id: str
    """The service's identifier, which is also its Compose service name."""
    name: str
    """What it is called in front of an operator."""
    profile: str
    """The profile that declared it."""
    state: ServiceState
    """What it is doing."""


type ServiceState = typing.Literal[
    "failed",
    "crash-looping",
    "unhealthy",
    "absent",
    "stopped",
    "starting",
    "running",
    "healthy",
    "host-managed",
]
"""What one service is actually doing.

Ordered from worst to best, so a form's condition is the minimum across its
services and needs no comparison table. The declaration order is therefore
load-bearing.
"""


__all__ = [
    "Service",
    "ServiceState",
]
