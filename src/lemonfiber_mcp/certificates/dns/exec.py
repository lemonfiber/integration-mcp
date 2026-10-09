# Copyright (c) 2026 NightWorksIO
"""The operator's own program, called with the record's name and value and nothing else."""

import os
import pathlib
import subprocess
from typing import TYPE_CHECKING, Final

from lemonfiber_mcp.certificates.dns.provider import ProviderError, Timing, needed
from lemonfiber_mcp.certificates.settings import TlsSettingsError

if TYPE_CHECKING:
    from collections.abc import Mapping

PATH: Final = "EXEC_PATH"
TIMEOUT_SECONDS: Final = 120
SEARCH_PATH: Final = "PATH"
"""The one setting the program is given, so it finds what it runs; no credential is."""


class Exec:
    """TXT records written by the operator's program: `<program> present <name> <value>`, and `cleanup` after."""

    timing = Timing()

    def __init__(self, program: pathlib.Path) -> None:
        """Hold the program, refusing one this user cannot run."""
        if not program.is_file() or not os.access(program, os.X_OK):
            msg = f"{PATH} names {program}, which is not a program this user can run."
            raise TlsSettingsError(msg)
        self._program = program

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]) -> Exec:
        """Return the provider its settings describe."""
        return cls(pathlib.Path(needed(environment, PATH)))

    def _run(self, step: str, name: str, value: str) -> None:
        environment = {SEARCH_PATH: os.environ.get(SEARCH_PATH, os.defpath)}
        try:
            subprocess.run(
                [str(self._program), step, name, value],
                env=environment,
                check=True,
                capture_output=True,
                timeout=TIMEOUT_SECONDS,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as failed:
            msg = f"{self._program} {step} failed: {type(failed).__name__}."
            raise ProviderError(msg) from None

    def present(self, name: str, value: str) -> None:
        """Ask the program to write the TXT record."""
        self._run("present", name, value)

    def cleanup(self, name: str, value: str) -> None:
        """Ask the program to remove the TXT record."""
        self._run("cleanup", name, value)
