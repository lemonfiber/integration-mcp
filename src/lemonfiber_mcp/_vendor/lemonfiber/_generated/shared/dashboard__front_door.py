# Copyright (c) 2026 NightWorksIO
"""The shapes `dashboard` and `front-door` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Address(typing.TypedDict):
    """Where the front door is reached, and what is worth knowing about the address."""

    caution: typing.NotRequired[str | None]
    """What is worth knowing about the address itself, where anything is. Absent
    for one that keeps working on its own.
    """
    url: str
    """The whole address, as it would be typed or followed."""


type Chosen = ChosenDerived | ChosenNamed | ChosenRefused
"""How the front door came to be the one it is."""


class ChosenDerived(typing.TypedDict):
    """Worked out from what the stack declares, which is what a stack whose
    operator has named nothing answers.
    """

    chosen: typing.Literal["derived"]


class ChosenNamed(typing.TypedDict):
    """Named by the operator, by the id the stack declares it under, and it is the
    door.
    """

    chosen: typing.Literal["named"]
    door: str


class ChosenRefused(typing.TypedDict):
    """Named by the operator and refused. The worked-out door stands, and this
    carries what was named and why it is not it.
    """

    chosen: typing.Literal["refused"]
    door: Refusal


type Facing = typing.Literal["asking", "watching", "shelf", "operators", "carriage", "unstated"]
"""What a service published to the local network is to the people in the house."""


class FrontDoorBeside(typing.TypedDict):
    """A service the household can reach that is not the front door, and why it is not.

    Carried rather than left out, because the decision is the useful part: an operator
    who can see that the index over every service was considered and refused has been
    told something, where one shown a single name has only been given an answer.
    """

    address: typing.NotRequired[Address | None]
    """The address to hand somebody for this service, read from this machine at the
    moment of asking rather than remembered.

    **Carried because not-the-door is not nowhere.** A household member wanting to
    watch something, or to ask for something, wants the service that faces them —
    and which of the two happens to be the front door is an operator's
    arrangement, not an answer to their question. Without this a surface can hand
    them only whichever one the door turned out to be, and say nothing at all
    about the other.

    Absent where the stack declares no port for it, for the reason the door's own
    address is absent then: an address with no port on it is one a browser answers
    with a refusal, and the manifest is where a port is declared.
    """
    because: str
    """Why it is not somewhere to begin."""
    facing: Facing
    """What it is to the household."""
    service: str
    """The service, by the name it shows itself under."""


class FrontDoorReport(typing.TypedDict):
    """The household's one front door: which service it is, where it stands, and what
    else they can reach that is not it.
    """

    address: typing.NotRequired[Address | None]
    """The address to hand them, read from this machine at the moment of asking
    rather than remembered. Absent where there is no door, and where there is
    one on a machine that will say neither what it is called nor where it is.
    """
    beside: list[FrontDoorBeside]
    """Everything else the household can reach, and why none of it is the door."""
    chosen: Chosen
    """How this came to be the door: worked out from what the stack declares, named
    by the operator, or named by them and refused.

    Carried as a state rather than left to the sentence beneath it, for the reason
    the standing is: an operator whose setting was refused reads the sentence, and
    a browser, a script or a dashboard reads this.
    """
    facing: typing.NotRequired[Facing | None]
    """What that service is to them. Absent for the same reason."""
    meaning: str
    """What this comes to, in the words an operator would say it in — including,
    where there is no door, that there is none.
    """
    service: typing.NotRequired[str | None]
    """The service the household begins at, by the name it shows itself under.
    Absent where this stack publishes nothing they could begin at.
    """
    standing: FrontDoorStanding
    """Where the front door stands."""


type FrontDoorStanding = typing.Literal["established", "library-only", "unreachable", "stranded", "none"]
"""Where the household's one front door stands."""


class Refusal(typing.TypedDict):
    """A named front door that is not one, and why it is not."""

    because: str
    """Why this stack will not send a household there."""
    named: str
    """What the operator recorded, as they wrote it."""


__all__ = [
    "Address",
    "Chosen",
    "ChosenDerived",
    "ChosenNamed",
    "ChosenRefused",
    "Facing",
    "FrontDoorBeside",
    "FrontDoorReport",
    "FrontDoorStanding",
    "Refusal",
]
