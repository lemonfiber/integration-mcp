# Copyright (c) 2026 NightWorksIO
"""The `plugins` envelope, and the shapes only `plugins` carries, gathered from its parts.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

from . import api_kind as _api_kind
from . import service_value as _service_value
from . import plugin_removal as _plugin_removal

from .api_kind import *
from .service_value import *
from .plugin_removal import *

__all__: list[str] = []
__all__ += _api_kind.__all__
__all__ += _service_value.__all__
__all__ += _plugin_removal.__all__
