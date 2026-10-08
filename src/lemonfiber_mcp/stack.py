# Copyright (c) 2026 NightWorksIO
"""Every call the server makes to the stack, each through the vendored client and nothing else.

A tool's arguments arrive checked against its schema, and are handed to the
client call its shape names. An action carried out answers with a job where its
work runs on; that job is followed for a while, and answered with its name
where it is still going.
"""

import base64
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, cast

from lemonfiber import Ended, Finished, Read, Running, StillRunningError

from lemonfiber_mcp.shapes import Reach

if TYPE_CHECKING:
    from collections.abc import Mapping

    from lemonfiber import AsyncClient, JobStanding, Json, Query

    from lemonfiber_mcp.shapes import ToolShape

FOLLOWED_FOR: Final = 45.0
"""How long an action's work is followed before the tool answers with its job's name."""
DRY_RUN: Final = "dry_run"
OFFER: Final = "offer"
JOB_KIND: Final = "job"
LOG_PARAMETERS: Final = {"service": "services", "form": "forms"}
"""Each repeatable log parameter, to the client argument it is given as."""
TAIL: Final = "tail"


class NotAWholeNumberError(ValueError):
    """A parameter that takes a whole number was given something else."""


@dataclass(frozen=True, slots=True)
class Bundle:
    """A file the stack handed over."""

    name: str
    content: bytes
    content_type: str | None

    def encoded(self) -> str:
        """Return the content as base64, the form a resource's blob carries."""
        return base64.b64encode(self.content).decode("ascii")


def whole(value: object, parameter: str) -> int:
    """Return a parameter given as a whole number, in either form JSON may carry it."""
    text = str(value).strip()
    if not text.isdigit():
        msg = f"`{parameter}` takes a whole number."
        raise NotAWholeNumberError(msg)
    return int(text)


STANDINGS: Final[Mapping[type[JobStanding], str]] = {Running: "running", Finished: "finished", Ended: "ended"}
"""What each place work can stand is called, as the answer says it."""


def standing(of: JobStanding) -> dict[str, object]:
    """Return where work stands, as data."""
    return {"job": of.job, "standing": STANDINGS[type(of)], "envelope": of.envelope}


async def read(client: AsyncClient, shape: ToolShape, arguments: Mapping[str, object]) -> object:
    """Ask for what a read tool reaches, and return the answer as data."""
    match shape.reach:
        case Reach.LOGS:
            lines = await client.logs(
                services=cast("list[str]", arguments.get("service", [])),
                forms=cast("list[str]", arguments.get("form", [])),
                tail=None if TAIL not in arguments else whole(arguments[TAIL], TAIL),
            )
            return {"lines": lines}
        case Reach.FILE:
            bundle = await client.bundle(str(arguments["name"]))
            return Bundle(bundle.name, bundle.content, bundle.content_type)
        case _:
            query = cast("Query", {name: arguments[name] for name in shape.parameters if name in arguments})
            return await client.read(Read(shape.target), query)


async def rehearse(client: AsyncClient, shape: ToolShape, arguments: Mapping[str, object]) -> object:
    """Ask an action what it would do, writing nothing."""
    return await client.act(shape.target, cast("Mapping[str, Json]", {**arguments, DRY_RUN: True}))


async def act(client: AsyncClient, shape: ToolShape, arguments: Mapping[str, object]) -> object:
    """Carry an action out, following its work for a while where it runs on."""
    answer = await client.act(shape.target, cast("Mapping[str, Json]", dict(arguments)))
    if answer["kind"] != JOB_KIND:
        return answer
    try:
        return standing(await client.follow(answer["data"]["job"], within=FOLLOWED_FOR))
    except StillRunningError:
        return standing(Running(answer["data"]["job"], answer))


async def job(client: AsyncClient, name: str) -> object:
    """Ask where the work a job's name stands for has got to."""
    return standing(await client.job(name))
