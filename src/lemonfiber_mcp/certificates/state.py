# Copyright (c) 2026 NightWorksIO
"""Where the certificate's state is kept: a directory only this user reads, written a whole file at a time.

The directory is `0700` and every file in it `0600`, owned by the user the
server runs as. A file is written beside its final name, flushed and renamed
into place, so a crash leaves the old file or the new one and never half of
either.
"""

import os
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    import pathlib

DIRECTORY_MODE: Final = 0o700
FILE_MODE: Final = 0o600
OTHERS: Final = 0o077
"""The permission bits that let anyone but the owner in."""


class StateError(Exception):
    """The state directory is not one the server may keep keys in."""


def kept(directory: pathlib.Path) -> pathlib.Path:
    """Return the state directory, made where it is missing, refusing one others can read or another user owns."""
    try:
        directory.mkdir(mode=DIRECTORY_MODE, parents=True, exist_ok=True)
        held = directory.stat()
    except OSError:
        msg = f"The state directory {directory} could not be made or read."
        raise StateError(msg) from None
    if held.st_uid != os.getuid():
        msg = f"The state directory {directory} is owned by another user."
        raise StateError(msg)
    if held.st_mode & OTHERS:
        msg = f"The state directory {directory} can be read by others; it holds keys, so it must be 0700."
        raise StateError(msg)
    return directory


def write(path: pathlib.Path, content: bytes) -> None:
    """Write a file whole, readable by this user alone, replacing what was there in one step."""
    path.parent.mkdir(mode=DIRECTORY_MODE, parents=True, exist_ok=True)
    beside = path.with_name(f".{path.name}.new")
    beside.unlink(missing_ok=True)
    with os.fdopen(os.open(beside, os.O_WRONLY | os.O_CREAT | os.O_EXCL, FILE_MODE), "wb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    beside.replace(path)
    folder = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(folder)
    finally:
        os.close(folder)
