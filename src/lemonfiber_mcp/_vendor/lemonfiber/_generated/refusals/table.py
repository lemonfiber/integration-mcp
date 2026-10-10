# Copyright (c) 2026 NightWorksIO
"""What the contract says of every refusal code, every family's gathered.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import types
import typing

from .admit_codes import ADMIT
from .ask_codes import ASK
from .gone_codes import GONE
from .life_codes import LIFE
from .listed import ListedRefusal, RefusalCode
from .migrate_codes import MIGRATE
from .play_codes import PLAY
from .plugin_codes import PLUGIN
from .rate_codes import RATE
from .read_codes import READ
from .repair_codes import REPAIR
from .restore_codes import RESTORE
from .serve_codes import SERVE
from .space_codes import SPACE
from .stack_codes import STACK
from .update_codes import UPDATE
from .wire_codes import WIRE

REFUSAL_CODES: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = types.MappingProxyType(
    {
        **ADMIT,
        **ASK,
        **GONE,
        **LIFE,
        **MIGRATE,
        **PLAY,
        **PLUGIN,
        **RATE,
        **READ,
        **REPAIR,
        **RESTORE,
        **SERVE,
        **SPACE,
        **STACK,
        **UPDATE,
        **WIRE,
    },
)
"""What the contract says of each refusal code."""


def is_refusal_code(value: str) -> typing.TypeIs[RefusalCode]:
    """Tell whether a code is one the contract lists as a refusal's."""
    return value in REFUSAL_CODES


__all__ = [
    "REFUSAL_CODES",
    "is_refusal_code",
]
