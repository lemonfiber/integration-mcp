# Copyright (c) 2026 NightWorksIO
"""DNS-01: the challenge's TXT record written through the operator's DNS provider, and seen at every authoritative server.

Providers are named, and their settings spelled, as lego names them, so an
operator's configuration carries over. A secret is read from the file its
`_FILE` setting names, never from the setting itself.
"""
