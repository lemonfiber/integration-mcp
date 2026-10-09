# Copyright (c) 2026 NightWorksIO
"""The `plugins` envelope, and the shapes only `plugins` carries, gathered from its parts.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

from . import api_kind as _api_kind
from . import plugin_step_adapter as _plugin_step_adapter
from . import plugin_installs as _plugin_installs

from .api_kind import *
from .plugin_step_adapter import *
from .plugin_installs import *

__all__: list[str] = []
__all__ += _api_kind.__all__
__all__ += _plugin_step_adapter.__all__
__all__ += _plugin_installs.__all__
