# Copyright (c) 2026 NightWorksIO
"""The `plugins` envelope, and the shapes only `plugins` carries, gathered from its parts.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

from . import expected as _expected
from . import plugin_reached_loopback as _plugin_reached_loopback
from . import wiring_contest as _wiring_contest

from .expected import *
from .plugin_reached_loopback import *
from .wiring_contest import *

__all__: list[str] = []
__all__ += _expected.__all__
__all__ += _plugin_reached_loopback.__all__
__all__ += _wiring_contest.__all__
