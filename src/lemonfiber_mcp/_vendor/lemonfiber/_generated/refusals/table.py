# Copyright (c) 2026 NightWorksIO
"""What the contract says of every refusal code, every family's gathered.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import types
import typing

from .admit_codes import ADMIT
from .ask_codes import ASK
from .bundle_codes import BUNDLE
from .device_codes import DEVICE
from .form_codes import FORM
from .gone_codes import GONE
from .key_codes import KEY
from .life_codes import LIFE
from .listed import ListedRefusal, RefusalCode
from .migrate_codes import MIGRATE
from .play_codes import PLAY
from .plugin_codes import PLUGIN
from .quota_codes import QUOTA
from .rate_codes import RATE
from .read_codes import READ
from .rehearse_codes import REHEARSE
from .repair_codes import REPAIR
from .restore_codes import RESTORE
from .serve_codes import SERVE
from .setting_codes import SETTING
from .setup_codes import SETUP
from .space_codes import SPACE
from .stack_codes import STACK
from .update_codes import UPDATE
from .wire_codes import WIRE
from .wish_codes import WISH
from .word_codes import WORD

REFUSAL_CODES: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = types.MappingProxyType(
    {
        **ADMIT,
        **ASK,
        **BUNDLE,
        **DEVICE,
        **FORM,
        **GONE,
        **KEY,
        **LIFE,
        **MIGRATE,
        **PLAY,
        **PLUGIN,
        **QUOTA,
        **RATE,
        **READ,
        **REHEARSE,
        **REPAIR,
        **RESTORE,
        **SERVE,
        **SETTING,
        **SETUP,
        **SPACE,
        **STACK,
        **UPDATE,
        **WIRE,
        **WISH,
        **WORD,
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
