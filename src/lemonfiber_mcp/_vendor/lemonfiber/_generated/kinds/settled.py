# Copyright (c) 2026 NightWorksIO
"""The `settled` envelope, and the shapes only `settled` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.protocols import Protocols


type SetUp = typing.Literal["none", "part-way", "done"]
"""Whether this stack is set up."""


class SettledEnvelope(typing.TypedDict):
    """The envelope carrying `settled`."""

    api_version: int
    data: SettledReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["settled"]


class SettledReport(typing.TypedDict):
    """What setup settled, read from the configuration as it stands, and whether this stack
    is set up.
    """

    data_root: typing.NotRequired[str | None]
    """Where the library is kept, a path on this machine or an NFS export as `DATA_ROOT`
    names it, or nothing where no data root is configured.
    """
    protocols: Protocols
    """Which ways of downloading are configured."""
    service_user: ServiceUser
    """The user and group the stack's services run as."""
    setup: SetUp
    """Whether this stack is set up."""


type UserFrom = typing.Literal["set", "part-set", "stack-owner"]
"""Where the user the services run as comes from."""


ServiceUser = typing.TypedDict(
    "ServiceUser",
    {
        "from": UserFrom,
        "gid": int,
        "uid": int,
    },
)
"""The user and group the stack's services run as."""


__all__ = [
    "ServiceUser",
    "SetUp",
    "SettledEnvelope",
    "SettledReport",
    "UserFrom",
]
