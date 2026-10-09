# Copyright (c) 2026 NightWorksIO
"""The shapes `config`, `credentials`, `doctor`, `outbound`, `plugins`, `wiring` and `wizard` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type ValueOrigin = (
    ValueOriginBundled
    | ValueOriginOperator
    | ValueOriginPlugin
    | ValueOriginUnknown
    | ValueOriginOverridden
    | ValueOriginOrphaned
)
"""Where a value in force came from.

Published under a name of its own because the generated schema keys on the type's
bare name, and a second `Origin` in the crate would be merged with this one into a
single definition carrying the variants of both — a published contract saying a
credential may be *unknown* and a setting may be *service*, neither of which is
true, and neither of which the additive-only surface check would refuse.
"""


class ValueOriginBundled(typing.TypedDict):
    """This build's own, out of what lemonfiber ships rather than out of a choice."""

    origin: typing.Literal["bundled"]


class ValueOriginOperator(typing.TypedDict):
    """The operator settled it, whether by answering for it or by editing it since."""

    origin: typing.Literal["operator"]


class ValueOriginOrphaned(typing.TypedDict):
    """A plugin set it and is no longer installed, and the value is still in force.

    Only where the record of what is installed was read and does not hold that
    plugin. A record that would not read cannot say a plugin is gone, so that is
    an unknown rather than this.
    """

    named: str
    """Which plugin set it."""
    origin: typing.Literal["orphaned"]


class ValueOriginOverridden(typing.TypedDict):
    """An installed plugin set it over a value that was there before, and that value
    is carried with it: what is in force and what it replaced are read together.
    """

    named: str
    """Which plugin set what is in force."""
    origin: typing.Literal["overridden"]
    replaced: ValueReplaced
    """What it replaced, and where that came from."""


class ValueOriginPlugin(typing.TypedDict):
    """A named plugin set it."""

    named: str
    """Which one, so the thread back to it is a name rather than a search."""
    origin: typing.Literal["plugin"]


class ValueOriginUnknown(typing.TypedDict):
    """It could not be established, and what stopped it."""

    origin: typing.Literal["unknown"]
    why: str
    """What stopped it being established, so the gap reads as a reason rather
    than as a shrug.
    """


ValueReplaced = typing.TypedDict(
    "ValueReplaced",
    {
        "from": ValueOrigin,
        "value": typing.NotRequired[str | None],
        "withheld": bool,
    },
)
"""The value a plugin's change replaced, and where that value came from.

Its own origin rather than assumed to be this build's default: before a plugin
set a value, the operator may have, or another plugin, and calling that value
*bundled* would tell somebody putting it back that they are returning to a
default when they are returning to a choice.
"""


__all__ = [
    "ValueOrigin",
    "ValueOriginBundled",
    "ValueOriginOperator",
    "ValueOriginOrphaned",
    "ValueOriginOverridden",
    "ValueOriginPlugin",
    "ValueOriginUnknown",
    "ValueReplaced",
]
