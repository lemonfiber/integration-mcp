# Copyright (c) 2026 NightWorksIO
"""The `plugins` envelope, and the shapes only `plugins` carries, gathered from its parts.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

from . import api_kind as _api_kind
from . import plugin_granting as _plugin_granting
from . import plugin_verification as _plugin_verification

from .api_kind import *
from .plugin_granting import *
from .plugin_verification import *

__all__: list[str] = []
__all__ += _api_kind.__all__
__all__ += _plugin_granting.__all__
__all__ += _plugin_verification.__all__
