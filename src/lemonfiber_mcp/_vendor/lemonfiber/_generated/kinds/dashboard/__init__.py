# Copyright (c) 2026 NightWorksIO
"""The `dashboard` envelope, and the shapes only `dashboard` carries, gathered from its parts.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

from . import affected as _affected
from . import dashboard_envelope as _dashboard_envelope

from .affected import *
from .dashboard_envelope import *

__all__: list[str] = []
__all__ += _affected.__all__
__all__ += _dashboard_envelope.__all__
