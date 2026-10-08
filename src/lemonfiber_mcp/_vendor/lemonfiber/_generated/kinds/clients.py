# Copyright (c) 2026 NightWorksIO
"""The `clients` envelope, and the shapes only `clients` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Cause(typing.TypedDict):
    """One thing that could be behind a symptom, and how to tell it from the others."""

    because: str
    """What is wrong."""
    fix: str
    """What to do about it."""
    tell: str
    """How to tell this cause from the others under the same symptom."""


class ClientsEnvelope(typing.TypedDict):
    """The envelope carrying `clients`."""

    api_version: int
    data: Guidance
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["clients"]


class Device(typing.TypedDict):
    """A kind of device somebody in the house might watch on."""

    caution: typing.NotRequired[str | None]
    """What is worth knowing before starting, where anything is."""
    client: str
    """What to use on it."""
    deep_link: typing.NotRequired[str | None]
    """A link that opens the app already pointed at this server, where the app is known to
    take one, with `{address}` where the server's address goes. Absent otherwise, and a
    hand-off then carries the address alone as its code, which the app is pointed at by
    scanning or typing.
    """
    device: str
    """What somebody would call the device they are holding."""
    instead: typing.NotRequired[str | None]
    """What to do instead where this is a bad device to be stuck with."""
    open_source: bool
    """Whether the app named is open source. A closed one may be named, with this false
    beside it, and is never the one recommended.
    """
    support: Support
    """How well served it is."""


class Guidance(typing.TypedDict):
    """The guidance in full, for a surface that shows all of it."""

    devices: list[Device]
    """Every device, in the order somebody is likely to be holding one."""
    nothing_is_installed: str
    """What this will not do for them."""
    only_at_home: str
    """True of every device, said once."""
    straining: typing.NotRequired[Straining | None]
    """Why playback here is likely to struggle before any app is chosen, or `None`
    where the preset in force asks for nothing this platform cannot serve.

    Absent far more often than present, and it must be: a caution shown to
    everybody says nothing about anybody's machine, and a reader who meets one
    every time stops reading it.
    """
    trouble: list[Trouble]
    """What to do when it does not work, keyed by the symptom."""


class Straining(typing.TypedDict):
    """Why playback here is likely to struggle, whatever app the household installs.

    Present only where the preset in force asks for transcoding this platform cannot
    do in hardware. It belongs to the guidance rather than to any one device: the
    preset and the platform decide it between them, and every device in the table
    meets it.
    """

    caution: str
    """What that preset asks of this machine, and what playback does where this
    machine cannot give it.
    """
    instead: str
    """What makes it stop."""
    preset: str
    """The preset in force, under the name it was chosen by."""


type Support = typing.Literal["good", "workable", "poor", "fallback"]
"""How well a device is served."""


class Trouble(typing.TypedDict):
    """Something somebody reports, and what is likely behind it.

    Keyed by the symptom rather than the cause: the person asking has the symptom,
    and which cause it is is the thing they cannot yet say.
    """

    causes: list[Cause]
    """What is likely behind it, most likely first."""
    symptom: str
    """What somebody says is happening, in their words."""


__all__ = [
    "Cause",
    "ClientsEnvelope",
    "Device",
    "Guidance",
    "Straining",
    "Support",
    "Trouble",
]
