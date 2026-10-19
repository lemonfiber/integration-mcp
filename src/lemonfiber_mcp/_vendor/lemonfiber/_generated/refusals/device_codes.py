# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `DEVICE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

DEVICE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "DEVICE-1": ListedRefusal(
        "NOT_A_DEVICE_NAME", 400, "Raised when a device key is asked for under a word that cannot name one."
    ),
    "DEVICE-10": ListedRefusal(
        "CHALLENGE_NOT_STANDING", 403, "Raised when a mint carries a challenge that does not stand."
    ),
    "DEVICE-11": ListedRefusal(
        "SIGNATURE_WRONG", 401, "Raised when a mint's signature does not verify against the device key."
    ),
    "DEVICE-12": ListedRefusal(
        "NO_CHALLENGE", 500, "Raised when this machine would not supply the bytes a challenge is made of."
    ),
    "DEVICE-13": ListedRefusal(
        "ATTESTATION_REVOKED",
        403,
        "Raised when an attestation's chain carries a certificate Google lists as revoked or suspended.",
    ),
    "DEVICE-2": ListedRefusal(
        "DEVICE_NAME_TAKEN",
        409,
        "Raised when a device key is registered under a name another device key holds.",
    ),
    "DEVICE-3": ListedRefusal(
        "PUBLIC_HALF_TAKEN",
        409,
        "Raised when a device key is registered with a public half another device key holds.",
    ),
    "DEVICE-4": ListedRefusal("NOT_P256", 400, "Raised when the public half given is not a P-256 key."),
    "DEVICE-5": ListedRefusal(
        "NO_ATTESTATION", 400, "Raised when a device key is registered with no attestation."
    ),
    "DEVICE-6": ListedRefusal(
        "ATTESTATION_UNVERIFIED",
        400,
        "Raised when an attestation does not verify, or does not cover the public half.",
    ),
    "DEVICE-7": ListedRefusal(
        "IN_SOFTWARE",
        400,
        "Raised when an attestation places the key in software, or says it was not made in the hardware that keeps it.",
    ),
    "DEVICE-8": ListedRefusal(
        "UNTRUSTED_APP", 403, "Raised when an attestation names an app this stack does not trust."
    ),
    "DEVICE-9": ListedRefusal(
        "NOT_REGISTERED", 404, "Raised when a device key named is not registered, or was revoked."
    ),
}
"""What the contract says of each `DEVICE` code."""
