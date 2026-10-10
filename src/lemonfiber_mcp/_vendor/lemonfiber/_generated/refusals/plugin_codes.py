# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `PLUGIN` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

PLUGIN: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "PLUGIN-10": ListedRefusal(
        "NOTHING_TO_REMOVE", 404, "Nothing by that name is installed on this machine."
    ),
    "PLUGIN-11": ListedRefusal(
        "NOTHING_TO_UPDATE", 404, "Nothing by that id is installed, so there is no version to replace."
    ),
    "PLUGIN-12": ListedRefusal(
        "STUCK", 500, "The version installed would not come off, so nothing else was touched."
    ),
    "PLUGIN-13": ListedRefusal(
        "ANSWERED",
        400,
        "Raised when a plugin's service would answer on a label another plugin's already does.",
    ),
    "PLUGIN-14": ListedRefusal(
        "TWO_SOURCES",
        400,
        "Raised when a plugin is installed from a source other than the one its name is already installed from.",
    ),
    "PLUGIN-15": ListedRefusal(
        "SOURCE_OFF",
        400,
        "Raised when a plugin is named from a git source and fetching from one is switched off.",
    ),
    "PLUGIN-16": ListedRefusal(
        "UNFETCHED", 500, "Raised when a git source could not be reached or would not hand over a revision."
    ),
    "PLUGIN-17": ListedRefusal(
        "NO_REVISION", 404, "Raised when a git source holds no branch, tag or commit by the name given."
    ),
    "PLUGIN-18": ListedRefusal(
        "CATALOGUE_OFF",
        400,
        "Raised when a plugin is installed by name and asking the catalogue is switched off.",
    ),
    "PLUGIN-19": ListedRefusal(
        "CATALOGUE_UNREACHABLE",
        500,
        "Raised when the catalogue's index or its signature could not be fetched.",
    ),
    "PLUGIN-2": ListedRefusal("UNREADABLE", 404, "The source names no plugin this build can read."),
    "PLUGIN-20": ListedRefusal(
        "SIGNATURE_UNVERIFIED",
        500,
        "Raised when the catalogue's index has no signature, one that does not verify, or none this build carries a key to check.",
    ),
    "PLUGIN-21": ListedRefusal(
        "CATALOGUE_UNREADABLE",
        500,
        "Raised when the catalogue's index verified and is not one this build reads.",
    ),
    "PLUGIN-22": ListedRefusal(
        "NOT_CATALOGUED", 404, "Raised when the catalogue holds no plugin by the name given."
    ),
    "PLUGIN-23": ListedRefusal(
        "NOT_AS_REVIEWED",
        500,
        "Raised when what the catalogue's origin served is not what the catalogue reviewed.",
    ),
    "PLUGIN-24": ListedRefusal(
        "SPELLED_ALIKE",
        400,
        "Raised when a plugin's service would be named, where lemonfiber keeps what a service holds, as another installed plugin's service already is.",
    ),
    "PLUGIN-25": ListedRefusal(
        "PLUGIN_OFFER_MOVED",
        400,
        "Raised when an install, an update or a removal answers an offer that was read against a plugin, a stack or a record that has since moved.",
    ),
    "PLUGIN-26": ListedRefusal(
        "UNAPPROVED",
        400,
        "Raised when a value a recipe would carry to a destination, or the egress guard's shape a service would take, was not approved as itself, or an approval names something the reading does not list.",
    ),
    "PLUGIN-27": ListedRefusal(
        "ANOTHER_PLUGIN",
        400,
        "Raised when the source an update names holds a different plugin from the one it was asked to update.",
    ),
    "PLUGIN-28": ListedRefusal(
        "OCCUPIED",
        400,
        "Raised when a plugin's service would take a name, a port or a label something already on this machine holds: a service of the stack or of the operator's overlay, another plugin's port, or a site in the proxy's live configuration.",
    ),
    "PLUGIN-29": ListedRefusal(
        "CATALOGUE_REPLACED",
        500,
        "Raised when the catalogue's index verifies and is older than the newest one this machine has verified.",
    ),
    "PLUGIN-3": ListedRefusal(
        "REFUSED", 400, "The manifest is read and this build refuses what it declares."
    ),
    "PLUGIN-30": ListedRefusal(
        "NEWEST_UNKEPT",
        500,
        "Raised when the record of the newest catalogue index this machine verified cannot be read or written.",
    ),
    "PLUGIN-31": ListedRefusal(
        "SCHEME_REFUSED",
        400,
        "Raised when a git source is named over a transport other than https, before anything is asked of it.",
    ),
    "PLUGIN-32": ListedRefusal(
        "ADDRESS_REFUSED",
        400,
        "Raised when a git source's host is, or stands for, an address on this machine or on a network of its own: loopback, private, link-local or unspecified.",
    ),
    "PLUGIN-33": ListedRefusal(
        "HEADER_NAMED",
        400,
        "Raised when a recipe substitutes a value into a header's name, which is a fixed identifier of the protocol and written out; the manifest's every other fault is listed beside it.",
    ),
    "PLUGIN-34": ListedRefusal(
        "INPUT_UNMATCHED",
        400,
        "Raised when a recipe of the act asks the operator for a value that was not given, or a value was given that no recipe of the act asks for.",
    ),
    "PLUGIN-35": ListedRefusal(
        "CALL_REFUSED",
        500,
        "Raised when a recipe's call was not sent because its host stands for an address not out on the internet; the install or update was put back.",
    ),
    "PLUGIN-36": ListedRefusal(
        "STEP_FAILED",
        500,
        "Raised when a recipe's step failed any other way \u2014 nothing answered, the answer was not the one it expects, a capture found nothing, or the answer was larger than a recipe reads; the install or update was put back.",
    ),
    "PLUGIN-37": ListedRefusal(
        "PATH_NOT_PLAIN",
        400,
        "Raised when a recipe's call path is not a plain absolute path; the manifest's every other fault is listed beside it.",
    ),
    "PLUGIN-38": ListedRefusal(
        "VALUE_WITHHELD",
        400,
        "Raised when a recipe's call was not sent because a value it carries may not go where it was going: not where its pairs say, not back to the service a credential belongs to, or outside without its approval; the install or update was put back.",
    ),
    "PLUGIN-4": ListedRefusal("UNRECORDED", 500, "The record of what is installed cannot be read."),
    "PLUGIN-5": ListedRefusal("ALREADY", 400, "The plugin is installed already."),
    "PLUGIN-6": ListedRefusal(
        "NOWHERE", 500, "There is no stack on this machine to put a plugin's container in."
    ),
    "PLUGIN-7": ListedRefusal(
        "UNWRITABLE", 500, "A directory or a document the install decided on would not land."
    ),
    "PLUGIN-8": ListedRefusal(
        "UNRECORDABLE", 500, "The wiring went down and the record of what is installed did not."
    ),
    "PLUGIN-9": ListedRefusal(
        "UNPROVED", 500, "The plugin's own service would not start, so nothing about it could be proved."
    ),
}
"""What the contract says of each `PLUGIN` code."""
