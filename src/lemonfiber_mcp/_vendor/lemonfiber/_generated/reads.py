# Copyright (c) 2026 NightWorksIO
"""Every read the web API serves, and what the contract says of each.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import enum
import types
import typing

from .envelope import Kind

API: typing.Final = "/api"
"""What every read's path begins with."""


class Read(enum.StrEnum):
    """A read lemonfiber serves answering with one envelope, named for its path.

    `READS` holds the kinds each answers with and the query parameters it takes.
    """

    VERSION = "version"
    """Answers with `version`."""
    FORMS = "forms"
    """Answers with `forms` or `preview`; takes `form` (more than once)."""
    STATUS = "status"
    """Answers with `status`."""
    SERVICES = "services"
    """Answers with `status`; takes `form` (more than once)."""
    CHECKS = "checks"
    """Answers with `doctor`; takes `only`."""
    STORAGE = "storage"
    """Answers with `doctor`."""
    REQUESTS = "requests"
    """Answers with `household`; takes `member` and `defaults`."""
    HELD = "held"
    """Answers with `held`; takes `member`, `defaults` and `most`."""
    HELD_ID = "held/{id}"
    """Answers with `title`, for the `id` in its path; takes `member` and `defaults`."""
    WATCHING = "watching"
    """Answers with `part-way`; takes `member` and `most`."""
    PLAYING = "playing"
    """Answers with `playing`; takes `member`."""
    HOSTING = "hosting"
    """Answers with `hosting`."""
    FRONT_DOOR = "front-door"
    """Answers with `front-door`."""
    NEWS = "news"
    """Answers with `news-items`."""
    TRACE = "trace"
    """Answers with `trace`; takes `term` and `season`."""
    STUCK = "stuck"
    """Answers with `stuck`."""
    CONFIG = "config"
    """Answers with `config`; takes `key`."""
    QUALITY = "quality"
    """Answers with `quality`."""
    EXPLAIN = "explain"
    """Answers with `glossary` or `word`; takes `word`."""
    BACKUPS = "backups"
    """Answers with `archives`."""
    OUTBOUND = "outbound"
    """Answers with `outbound`."""
    PROVENANCE = "provenance"
    """Answers with `provenance`."""
    CATALOGUE = "catalogue"
    """Answers with `catalogue`."""
    STORED = "stored"
    """Answers with `stored`."""
    UNINSTALL = "uninstall"
    """Answers with `uninstall`; takes `tier`."""
    SPACE = "space"
    """Answers with `space`."""
    BANDWIDTH = "bandwidth"
    """Answers with `bandwidth`."""
    CLIENTS = "clients"
    """Answers with `clients`."""
    ALERTS = "alerts"
    """Answers with `alerts`."""
    CREDENTIALS = "credentials"
    """Answers with `credentials`."""
    MIGRATION = "migration"
    """Answers with `migration`."""
    HISTORY = "history"
    """Answers with `history`."""
    UPDATE = "update"
    """Answers with `self-update` or `update`; takes `what` and `to`."""
    PLUGINS = "plugins"
    """Answers with `plugins`."""
    WIRING = "wiring"
    """Answers with `wiring`."""

    @property
    def path(self) -> str:
        """Return the path this read is served on, each segment a caller fills written as `{name}`."""
        return f"{API}/{self.value}"


LOGS: typing.Final = "/api/logs"
"""Answers one envelope a line, each `job` or `log`; takes `form` (more than once), `service` (more than once), `tail` and `follow`."""

BUNDLE: typing.Final = "/api/bundle"
"""Answers with a file, named by `name` in the path."""

HELD_ID_POSTER: typing.Final = "/api/held/{id}/poster"
"""Answers with a file, for the `id` in its path; takes `member` and `defaults`."""

HELD_ID_BACKDROP: typing.Final = "/api/held/{id}/backdrop"
"""Answers with a file, for the `id` in its path; takes `member` and `defaults`."""


class ReadParameter(typing.NamedTuple):
    """One query parameter a read takes."""

    name: str
    """Its name in the query."""
    repeatable: bool
    """Whether it may be given more than once."""


class Readable(typing.NamedTuple):
    """What the contract says of one read."""

    kinds: tuple[Kind, ...]
    """Every kind it may answer with."""
    parameters: tuple[ReadParameter, ...]
    """Every query parameter it takes, in the order the contract lists them."""
    segments: tuple[str, ...] = ()
    """Every segment of its path a caller fills, by name."""


READS: typing.Final[typing.Mapping[Read, Readable]] = types.MappingProxyType(
    {
        Read.VERSION: Readable(("version",), ()),
        Read.FORMS: Readable(("forms", "preview"), (ReadParameter("form", True),)),
        Read.STATUS: Readable(("status",), ()),
        Read.SERVICES: Readable(("status",), (ReadParameter("form", True),)),
        Read.CHECKS: Readable(("doctor",), (ReadParameter("only", False),)),
        Read.STORAGE: Readable(("doctor",), ()),
        Read.REQUESTS: Readable(
            ("household",), (ReadParameter("member", False), ReadParameter("defaults", False))
        ),
        Read.HELD: Readable(
            ("held",),
            (ReadParameter("member", False), ReadParameter("defaults", False), ReadParameter("most", False)),
        ),
        Read.HELD_ID: Readable(
            ("title",), (ReadParameter("member", False), ReadParameter("defaults", False)), ("id",)
        ),
        Read.WATCHING: Readable(
            ("part-way",), (ReadParameter("member", False), ReadParameter("most", False))
        ),
        Read.PLAYING: Readable(("playing",), (ReadParameter("member", False),)),
        Read.HOSTING: Readable(("hosting",), ()),
        Read.FRONT_DOOR: Readable(("front-door",), ()),
        Read.NEWS: Readable(("news-items",), ()),
        Read.TRACE: Readable(("trace",), (ReadParameter("term", False), ReadParameter("season", False))),
        Read.STUCK: Readable(("stuck",), ()),
        Read.CONFIG: Readable(("config",), (ReadParameter("key", False),)),
        Read.QUALITY: Readable(("quality",), ()),
        Read.EXPLAIN: Readable(("glossary", "word"), (ReadParameter("word", False),)),
        Read.BACKUPS: Readable(("archives",), ()),
        Read.OUTBOUND: Readable(("outbound",), ()),
        Read.PROVENANCE: Readable(("provenance",), ()),
        Read.CATALOGUE: Readable(("catalogue",), ()),
        Read.STORED: Readable(("stored",), ()),
        Read.UNINSTALL: Readable(("uninstall",), (ReadParameter("tier", False),)),
        Read.SPACE: Readable(("space",), ()),
        Read.BANDWIDTH: Readable(("bandwidth",), ()),
        Read.CLIENTS: Readable(("clients",), ()),
        Read.ALERTS: Readable(("alerts",), ()),
        Read.CREDENTIALS: Readable(("credentials",), ()),
        Read.MIGRATION: Readable(("migration",), ()),
        Read.HISTORY: Readable(("history",), ()),
        Read.UPDATE: Readable(
            ("self-update", "update"), (ReadParameter("what", False), ReadParameter("to", False))
        ),
        Read.PLUGINS: Readable(("plugins",), ()),
        Read.WIRING: Readable(("wiring",), ()),
    }
)
"""What the contract says of each read answering with one envelope, in the order it lists them."""


__all__ = [
    "API",
    "BUNDLE",
    "HELD_ID_BACKDROP",
    "HELD_ID_POSTER",
    "LOGS",
    "READS",
    "Read",
    "ReadParameter",
    "Readable",
]
