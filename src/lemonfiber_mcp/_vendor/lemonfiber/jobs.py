# Copyright (c) 2026 NightWorksIO
"""Where the work one name stands for got to.

An action that reaches the services answers with a name rather than an
outcome, and the name is redeemed afterwards. The standing is carried by the
status and the kind together: `202` is work still going, `200` with the
command's own kind is work that finished, and `200` with the `job` kind is work
that ended before it finished.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lemonfiber._generated import Envelope, JobEnvelope


@dataclass(frozen=True, slots=True)
class Running:
    """The work is still going; `envelope` is the one the accepting reply carried."""

    job: str
    envelope: JobEnvelope


@dataclass(frozen=True, slots=True)
class Finished:
    """The work finished; `envelope` is what the equivalent command answers with."""

    job: str
    envelope: Envelope


@dataclass(frozen=True, slots=True)
class Ended:
    """The work ended before it finished: its name was released, or it was let go because nothing asked."""

    job: str
    envelope: JobEnvelope


type JobStanding = Running | Finished | Ended
"""One of the three places work can stand; a failure is raised instead."""
