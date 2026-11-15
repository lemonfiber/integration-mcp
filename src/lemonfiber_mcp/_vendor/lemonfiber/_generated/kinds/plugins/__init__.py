# Copyright (c) 2026 NightWorksIO
"""The `plugins` envelope, and the shapes only `plugins` carries, gathered from its parts.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

from . import expected as _expected
from . import plugin_reached_proxied as _plugin_reached_proxied
from . import plugin_install as _plugin_install

from .expected import *
from .plugin_reached_proxied import *
from .plugin_install import *

__all__: list[str] = []
__all__ += _expected.__all__
__all__ += _plugin_reached_proxied.__all__
__all__ += _plugin_install.__all__
