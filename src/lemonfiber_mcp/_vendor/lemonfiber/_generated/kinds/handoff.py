# Copyright (c) 2026 NightWorksIO
"""The `handoff` envelope, and the shapes only `handoff` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class HandoffClient(typing.TypedDict):
    """One app a device can be pointed at the stack with, and the code that points it."""

    client: str
    """What to use on it."""
    code: str
    """What the code for this app carries: a link that opens the app at this server where
    the app takes one, and the server's address otherwise.
    """
    deep_link: bool
    """Whether [`code`](Self::code) is such a link rather than the address alone."""
    device: str
    """What somebody would call the device they are holding."""
    open_source: bool
    """Whether that app is open source. A closed one is never the recommended path."""


class HandoffEnvelope(typing.TypedDict):
    """The envelope carrying `handoff`."""

    api_version: int
    data: HandoffReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["handoff"]


type HandoffRemedy = typing.Literal["invite", "ask-again", "start-server", "record-address"]
"""What there is to do next about a hand-off, which each surface says in its own words.

Carried as a name rather than as a sentence because the act is the same everywhere
and the way to take it is not: a terminal names a command, and an app offers a
control. A sentence written here would have to pick one of them, and every other
surface would then be showing somebody an instruction it cannot carry out.
"""


class HandoffReport(typing.TypedDict):
    """Where one person's hand-off stands, and what to hand them.

    **The code is an address and nothing more.** Whoever holds a copy of it can find the
    server and still has to sign in as somebody, so a code sent to the wrong phone, or
    photographed over a shoulder, gives away where the server is and nothing else.
    """

    address: typing.NotRequired[str | None]
    """The address the code carries. Absent where there is no address to carry, which is
    one of the ways a hand-off fails.
    """
    caution: typing.NotRequired[str | None]
    """What is worth knowing about that address, where anything is: most often that it
    answers only on the home network.
    """
    clients: list[HandoffClient]
    """The apps to point a device at the stack with, each with its code."""
    issued: typing.NotRequired[str | None]
    """When a code was first issued for them, as an instant. Absent until one is."""
    name: str
    """Who it is for, as the media server spells their account where it holds one, and as
    it was asked for otherwise.
    """
    quick_connect: bool
    """Whether the media server offers the sign-in by short code, where one account already
    signed in approves another device.
    """
    reason: typing.NotRequired[str | None]
    """Why it stands there, where that is not the state itself: why an account that is not
    there stops it, and what stopped one that failed. In words any surface can show, so
    it names no command; what to do about it is [`remedy`](Self::remedy).
    """
    rehearsed: bool
    """Whether this was a rehearsal, in which no issue was written down."""
    remedy: typing.NotRequired[HandoffRemedy | None]
    """What there is to do next, where there is anything: named rather than said, so
    that each surface offers it in its own way.
    """
    sessions: list[HandoffSession]
    """The devices signed in to the account now, as the media server lists them."""
    state: HandoffState
    """Where it stands."""
    steps: list[str]
    """How the person signs in on the new device, one step at a time.

    Every step is something the person does on their device, in words any surface can
    show. Asking again afterwards is not one of them: that is [`remedy`](Self::remedy).

    **Guidance and never an approval.** Where the sign-in asks for a short code to be
    approved from a device they are already signed in on, that approval is theirs: it
    is the step that proves the person holding the new device is the person the
    account is for, and a program that took it for them would have proved nothing.
    """


class HandoffSession(typing.TypedDict):
    """One device the media server lists as signed in to the account."""

    client: str
    """The app it signed in with."""
    device: str
    """What the device calls itself."""
    last_seen: typing.NotRequired[str | None]
    """When the media server last heard from it, where it says."""


type HandoffState = typing.Literal["unprovisioned", "ready", "pending", "connected", "failed"]
"""Where one person's hand-off stands.

Read from the media server each time rather than remembered, apart from when a code
was first issued and which devices were signed in then: whether a device is signed in
is the server's to say, and a copy kept here would go on saying it after the person
signed out.
"""


__all__ = [
    "HandoffClient",
    "HandoffEnvelope",
    "HandoffRemedy",
    "HandoffReport",
    "HandoffSession",
    "HandoffState",
]
