# Copyright (c) 2026 NightWorksIO
"""The `plugins` envelope, and the shapes only `plugins` carries, gathered from its parts.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

from . import api_kind as _api_kind
from . import plugin_failing_as_declared as _plugin_failing_as_declared
from . import plugin_install as _plugin_install

from .api_kind import *
from .plugin_failing_as_declared import *
from .plugin_install import *

__all__: list[str] = []
__all__ += _api_kind.__all__
__all__ += _plugin_failing_as_declared.__all__
__all__ += _plugin_install.__all__
