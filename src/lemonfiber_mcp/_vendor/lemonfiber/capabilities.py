# Copyright (c) 2026 NightWorksIO
"""What a stack says it can do, for the credential that asked.

`GET /api/capabilities` names every request the stack serves by the path it is
served at, `/api/actions/<name>` for an action and `/api/<name>` for a read,
each with what it comes to for the credential that asked: `available`,
`unconfigured` (a setting has to be turned on first) or `unpermitted` (this
credential may not ask for it). A request the stack does not have is absent.
It is a reading like any other: it can change while a client holds it, so it
carries when it was read.
"""

import typing
from dataclasses import dataclass

from lemonfiber._generated import CapabilityState
from lemonfiber.reads import ACTIONS

if typing.TYPE_CHECKING:
    import datetime
    from collections.abc import Mapping

    from lemonfiber.reads import Read

STATES: typing.Final[frozenset[CapabilityState]] = frozenset(typing.get_args(CapabilityState.__value__))
"""Every state the contract says a capability can be in."""


@dataclass(frozen=True, slots=True)
class CapabilitySet:
    """Every capability a stack has, by path, as it stood for this credential when it was read."""

    states: Mapping[str, CapabilityState]
    """Each capability's path, to what it comes to for the credential that asked."""
    read_at: datetime.datetime
    """When the answer arrived, in UTC. A set not read again lately is an opinion, not a fact."""

    def of(self, path: str) -> CapabilityState | None:
        """Return what the capability served at `path` comes to, or None where the stack does not have it."""
        return self.states.get(path)

    def of_action(self, action: str) -> CapabilityState | None:
        """Return what the action comes to, or None where the stack does not have it."""
        return self.of(f"{ACTIONS}/{action}")

    def of_read(self, read: Read) -> CapabilityState | None:
        """Return what the read comes to, or None where the stack does not have it."""
        return self.of(read.path)

    def in_state(self, state: CapabilityState) -> frozenset[str]:
        """Return the path of every capability in `state`."""
        return frozenset(path for path, held in self.states.items() if held == state)

    @property
    def available(self) -> frozenset[str]:
        """Every capability this credential may use now."""
        return self.in_state("available")

    @property
    def unconfigured(self) -> frozenset[str]:
        """Every capability the stack has behind a setting that is switched off."""
        return self.in_state("unconfigured")

    @property
    def unpermitted(self) -> frozenset[str]:
        """Every capability the stack has and this credential may not ask for: what its scope does not reach."""
        return self.in_state("unpermitted")


def is_state(value: object) -> typing.TypeIs[CapabilityState]:
    """Tell whether a value is a state the contract lists."""
    return isinstance(value, str) and value in STATES
