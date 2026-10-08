# Copyright (c) 2026 NightWorksIO
"""The `restore` envelope, and the shapes only `restore` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.backup__restore import Scope


class BackupManifest(typing.TypedDict):
    """The record written inside an archive, and read back to decide a restore.

    Everything a restore needs to know before it overwrites anything: what made
    the archive, when, what data root it was taken against, what it covers, whether
    it is sensitive, and the contents to list. Round-trips through JSON so the same
    value the capture wrote is the value the restore reads.
    """

    created_at: str
    """When it was taken. Opaque here; the surface stamps it from the clock."""
    data_root: str
    """The data root it was taken against, to notice a restore to a different one."""
    members: list[Member]
    """What is inside, for a listing shown before anything is overwritten."""
    product_version: str
    """The lemonfiber version that wrote it, checked against the one restoring."""
    schema: int
    """The archive format, checked before anything inside is trusted."""
    scope: Scope
    """What it covers."""
    sensitive: bool
    """Whether it carries credentials, and so must be handled as sensitive."""


class Member(typing.TypedDict):
    """One entry in an archive's contents listing."""

    archive_path: str
    """Where it sits inside the archive."""
    label: str
    """What it is, in the operator's terms."""


class Preview(typing.TypedDict):
    """What a restore would do, shown before anything is overwritten."""

    agreement: str
    """What this listing is, so consent given for it can name which listing it read.

    Carried on every listing rather than only on the ones that would re-point
    something: a surface that has to look for it is a surface that can fail to
    find it, and a restore that would overwrite the same configuration in place
    is still one somebody may agree to.
    """
    downgrade: bool
    """Whether the archive is old enough that a compatibility warning applies."""
    manifest: BackupManifest
    """The archive's own account of itself — its scope, version and contents."""
    relocation: typing.NotRequired[Relocation | None]
    """The data-root difference, where the archive was taken against another one."""


class Relocation(typing.TypedDict):
    """A restore whose archive was taken against a different data root than the one
    configured now, so its stored paths would land where nothing exists.
    """

    now: str
    """The data root configured now."""
    was: str
    """The data root the archive was taken against."""


class Restoration(typing.TypedDict):
    """What a restore said: what it would overwrite, and whether it did.

    The listing is present either way, and that is the point of the shape. It is not
    a separate request a surface may or may not make — it is the half of a restore
    that happens before anything is overwritten, so every answer carries it and an
    answer that overwrote nothing is one whose `done` is absent.
    """

    done: typing.NotRequired[RestoreReport | None]
    """What was put back, or nothing where nothing was."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    would: Preview
    """What the archive holds and what restoring it would come to, read before
    anything was touched.
    """


class RestoreEnvelope(typing.TypedDict):
    """The envelope carrying `restore`."""

    api_version: int
    data: Restoration
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["restore"]


class RestoreReport(typing.TypedDict):
    """What a restore did."""

    from_version: str
    """The lemonfiber version the archive was written by."""
    relocated: typing.NotRequired[Relocation | None]
    """The data root that was re-pointed, where the restore accepted one."""
    scope: Scope
    """What was restored."""


__all__ = [
    "BackupManifest",
    "Member",
    "Preview",
    "Relocation",
    "Restoration",
    "RestoreEnvelope",
    "RestoreReport",
]
