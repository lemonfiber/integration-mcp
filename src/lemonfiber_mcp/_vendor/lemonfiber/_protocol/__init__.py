# Copyright (c) 2026 NightWorksIO
"""What goes on the wire and what comes back, read the same way by both clients.

Nothing here performs I/O. Each `Operation` pairs the `Call` a client sends
with the reading of the `Answer` that comes back, so a client sends the call
over its own transport and hands the answer to the operation: everything a
request carries and everything an answer means is decided here, once.
"""
