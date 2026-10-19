# Copyright (c) 2026 NightWorksIO
"""The `plugins` envelope, and the shapes only `plugins` carries, gathered from its parts.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

from . import api_kind as _api_kind
from . import service_url_of as _service_url_of
from . import plugin_nonconforming as _plugin_nonconforming

from .api_kind import *
from .service_url_of import *
from .plugin_nonconforming import *

__all__: list[str] = []
__all__ += _api_kind.__all__
__all__ += _service_url_of.__all__
__all__ += _plugin_nonconforming.__all__
