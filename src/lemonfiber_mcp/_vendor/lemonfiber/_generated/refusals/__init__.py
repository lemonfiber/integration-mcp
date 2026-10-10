# Copyright (c) 2026 NightWorksIO
"""Every code the contract lists a refusal as carrying, and what it says of each.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

from . import listed as _listed
from . import table as _table

from .listed import *
from .table import *

__all__: list[str] = []
__all__ += _listed.__all__
__all__ += _table.__all__
