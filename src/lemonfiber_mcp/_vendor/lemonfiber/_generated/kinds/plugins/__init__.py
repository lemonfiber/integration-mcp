# Copyright (c) 2026 NightWorksIO
"""The `plugins` envelope, and the shapes only `plugins` carries, gathered from its parts.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

from . import expected as _expected
from . import plugin_reached_household as _plugin_reached_household
from . import plugin_taking as _plugin_taking

from .expected import *
from .plugin_reached_household import *
from .plugin_taking import *

__all__: list[str] = []
__all__ += _expected.__all__
__all__ += _plugin_reached_household.__all__
__all__ += _plugin_taking.__all__
