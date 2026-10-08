# Copyright (c) 2026 NightWorksIO
"""Every action an integration key may call, and what the contract says of each.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import types
import typing

type KeyCallableAction = typing.Literal[
    "restart", "diagnose", "update", "downloads-pause", "downloads-resume"
]
"""Every action a key may call; any other is refused to a key, naming its scope."""


class KeyCallable(typing.NamedTuple):
    """What the contract says of one action a key may call."""

    disturbs: bool
    """Whether calling it disturbs the running system."""
    rehearsal: bool
    """Whether it takes `dry_run`, so it can be rehearsed before the real call is offered."""
    idempotent: bool
    """Whether calling it again with the same arguments leaves the stack as calling it once did."""


KEY_CALLABLE: typing.Final[typing.Mapping[KeyCallableAction, KeyCallable]] = types.MappingProxyType(
    {
        "restart": KeyCallable(True, True, True),
        "diagnose": KeyCallable(True, False, False),
        "update": KeyCallable(True, True, False),
        "downloads-pause": KeyCallable(False, True, True),
        "downloads-resume": KeyCallable(False, True, True),
    }
)
"""What the contract says of each action a key may call, in the order it lists them."""


def is_key_callable(value: str) -> typing.TypeIs[KeyCallableAction]:
    """Tell whether an action is one the contract says a key may call."""
    return value in KEY_CALLABLE


__all__ = [
    "KEY_CALLABLE",
    "KeyCallable",
    "KeyCallableAction",
    "is_key_callable",
]
