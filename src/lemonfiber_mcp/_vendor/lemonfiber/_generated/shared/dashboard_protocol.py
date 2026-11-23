# Copyright (c) 2026 NightWorksIO
"""The shapes `dashboard` and `in-flight` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type DashboardProtocol = typing.Literal["usenet", "torrent"]
"""Which protocol a transfer is moving over, since the same download reads
differently on each — a Usenet download has no peers, a torrent has no server.
"""


__all__ = [
    "DashboardProtocol",
]
