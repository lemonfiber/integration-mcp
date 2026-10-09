# Copyright (c) 2026 NightWorksIO
"""Every code the contract lists a refusal as carrying, and what it says of each.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import types
import typing

type RefusalCode = typing.Literal[
    "ADMIT-10",
    "ADMIT-11",
    "ADMIT-12",
    "ADMIT-4",
    "ADMIT-5",
    "ADMIT-6",
    "ADMIT-7",
    "ADMIT-8",
    "ADMIT-9",
    "ASK-1",
    "ASK-10",
    "ASK-11",
    "ASK-12",
    "ASK-13",
    "ASK-2",
    "ASK-3",
    "ASK-4",
    "ASK-5",
    "ASK-6",
    "ASK-7",
    "ASK-8",
    "ASK-9",
    "GONE-2",
    "LIFE-10",
    "MIGRATE-1",
    "PLUGIN-10",
    "PLUGIN-11",
    "PLUGIN-12",
    "PLUGIN-13",
    "PLUGIN-14",
    "PLUGIN-15",
    "PLUGIN-16",
    "PLUGIN-17",
    "PLUGIN-18",
    "PLUGIN-19",
    "PLUGIN-2",
    "PLUGIN-20",
    "PLUGIN-21",
    "PLUGIN-22",
    "PLUGIN-23",
    "PLUGIN-24",
    "PLUGIN-25",
    "PLUGIN-26",
    "PLUGIN-27",
    "PLUGIN-28",
    "PLUGIN-29",
    "PLUGIN-3",
    "PLUGIN-30",
    "PLUGIN-31",
    "PLUGIN-32",
    "PLUGIN-33",
    "PLUGIN-34",
    "PLUGIN-35",
    "PLUGIN-36",
    "PLUGIN-37",
    "PLUGIN-38",
    "PLUGIN-4",
    "PLUGIN-5",
    "PLUGIN-6",
    "PLUGIN-7",
    "PLUGIN-8",
    "PLUGIN-9",
    "RATE-6",
    "READ-1",
    "READ-10",
    "READ-11",
    "READ-12",
    "READ-13",
    "READ-14",
    "READ-15",
    "READ-16",
    "READ-2",
    "READ-3",
    "READ-4",
    "READ-5",
    "READ-6",
    "READ-7",
    "READ-8",
    "READ-9",
    "REPAIR-1",
    "RESTORE-11",
    "SERVE-6",
    "SERVE-7",
    "SERVE-8",
    "SPACE-6",
    "STACK-1",
    "STACK-10",
    "STACK-2",
    "STACK-3",
    "STACK-4",
    "STACK-5",
    "STACK-6",
    "STACK-7",
    "STACK-8",
    "STACK-9",
    "UPDATE-5",
    "WIRE-1",
    "WIRE-2",
    "WIRE-3",
    "WIRE-4",
    "WIRE-5",
    "WIRE-6",
    "WIRE-7",
]
"""Every code a refusal may carry."""


class ListedRefusal(typing.NamedTuple):
    """What the contract says of one refusal code."""

    name: str
    """The code's name in the core's registry."""
    status: int
    """The one status the refusal is answered with."""
    description: str
    """The registry's own line about it."""


REFUSAL_CODES: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = types.MappingProxyType(
    {
        "ADMIT-10": ListedRefusal(
            "NOT_A_PASSWORD", 400, "Raised when what was offered at the door is not a password."
        ),
        "ADMIT-11": ListedRefusal(
            "KEY_IN_THE_CLEAR",
            403,
            "Raised when a key arrived from another machine over a connection its pin does not verify.",
        ),
        "ADMIT-12": ListedRefusal(
            "NOT_FOR_A_KEY", 403, "Raised when a key asked for something its scope does not reach."
        ),
        "ADMIT-4": ListedRefusal(
            "NOT_ADMITTED", 403, "Raised when a request carried no token, session or key this run admits."
        ),
        "ADMIT-5": ListedRefusal(
            "ELSEWHERE", 403, "Raised when a request said it came from somewhere this server is not."
        ),
        "ADMIT-6": ListedRefusal(
            "NOT_YOURS", 403, "Raised when an account asked for something that is not its to ask for."
        ),
        "ADMIT-7": ListedRefusal(
            "UNCONFIRMED", 403, "Raised when the media server could not say whether an account is still one."
        ),
        "ADMIT-8": ListedRefusal(
            "NOT_THE_PASSWORD", 401, "Raised when the password offered at the door was wrong, or none is set."
        ),
        "ADMIT-9": ListedRefusal(
            "TOO_MANY_ATTEMPTS", 429, "Raised when the door has been given too many wrong passwords lately."
        ),
        "ASK-1": ListedRefusal(
            "NO_SUCH_ACTION", 404, "Raised where no action goes by the name that was asked for."
        ),
        "ASK-10": ListedRefusal(
            "WRONG_METHOD", 405, "Raised where an endpoint was asked with a method it does not answer."
        ),
        "ASK-11": ListedRefusal(
            "NOT_A_KEY_REQUEST",
            400,
            "Raised where the body of a mint is not a key's name, scope, purpose and the password.",
        ),
        "ASK-12": ListedRefusal(
            "NOT_AN_IDEMPOTENCY_KEY",
            400,
            "Raised where an action's `Idempotency-Key` is not one to 255 visible characters, or is given more than once.",
        ),
        "ASK-13": ListedRefusal(
            "IDEMPOTENCY_KEY_REUSED",
            400,
            "Raised where an `Idempotency-Key` already sent with one action and its arguments is sent with another.",
        ),
        "ASK-2": ListedRefusal(
            "MISSING_ARGUMENT", 400, "Raised where an action was not given an argument it needs."
        ),
        "ASK-3": ListedRefusal(
            "UNRECOGNISED_ARGUMENT", 400, "Raised where an argument was given a value that names nothing."
        ),
        "ASK-4": ListedRefusal(
            "UNWANTED_ARGUMENT",
            400,
            "Raised where an action was given an argument its command has nowhere to put.",
        ),
        "ASK-5": ListedRefusal(
            "ARGUMENTS_TOGETHER",
            400,
            "Raised where two arguments that each name a different request arrived together.",
        ),
        "ASK-6": ListedRefusal(
            "NOT_ARGUMENTS", 400, "Raised where the body of an action is not arguments it can read."
        ),
        "ASK-7": ListedRefusal(
            "NO_SUCH_JOB", 404, "Raised where a job was asked about that this run did not start."
        ),
        "ASK-8": ListedRefusal(
            "NOT_AN_ANSWER", 400, "Raised where the body of a setup step is not an answer it can read."
        ),
        "ASK-9": ListedRefusal(
            "NO_ENDPOINT", 404, "Raised where a path under the endpoints is one no endpoint answers."
        ),
        "GONE-2": ListedRefusal(
            "ANOTHER_READING",
            400,
            "Raised when an agreement names a reading of this machine that is not the one standing now.",
        ),
        "LIFE-10": ListedRefusal(
            "RESTART_MOVED",
            400,
            "Raised where a restart names an offer that is not the one a fresh look at the stack builds.",
        ),
        "MIGRATE-1": ListedRefusal(
            "OFFER_MOVED",
            400,
            "Raised when a replacement was agreed to for an offer that is not the one standing now.",
        ),
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
            "UNFETCHED",
            500,
            "Raised when a git source could not be reached or would not hand over a revision.",
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
            "Raised when a value a recipe would carry to a destination was not approved as itself, or an approval names a pair the recipe does not carry.",
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
        "RATE-6": ListedRefusal(
            "PAUSING_MOVED",
            400,
            "Raised where pausing or resuming the download clients names an offer that is not the one a fresh look at them builds.",
        ),
        "READ-1": ListedRefusal(
            "UNWANTED", 400, "Raised where a read was given a parameter its answer has nowhere to put."
        ),
        "READ-10": ListedRefusal(
            "TOO_MANY_AT_ONCE", 400, "Raised where more holdings were asked for than one read answers with."
        ),
        "READ-11": ListedRefusal(
            "NO_SUCH_GROUP", 400, "Raised where a diagnosis was narrowed to a group or check that is not one."
        ),
        "READ-12": ListedRefusal(
            "NO_SUCH_REMOVAL", 400, "Raised where a removal was named that is none of the four there are."
        ),
        "READ-13": ListedRefusal(
            "NO_UPDATE_OBJECT",
            400,
            "Raised where moving forward was asked about and neither stack nor self named.",
        ),
        "READ-14": ListedRefusal(
            "NOT_A_LINE_COUNT",
            400,
            "Raised where how many log lines to begin with is not a number within the ceiling.",
        ),
        "READ-15": ListedRefusal(
            "NOT_A_CHOICE",
            400,
            "Raised where a parameter that takes a yes or a no is neither true nor false.",
        ),
        "READ-16": ListedRefusal(
            "MEMBER_AND_DEFAULTS",
            400,
            "Raised where a household read named a member and asked for the household's defaults as well.",
        ),
        "READ-2": ListedRefusal(
            "REPEATED", 400, "Raised where a parameter carrying one value was given more than once."
        ),
        "READ-3": ListedRefusal(
            "NO_SUCH_READ", 404, "Raised where no read goes by the name that was asked for."
        ),
        "READ-4": ListedRefusal(
            "NO_TERM", 400, "Raised where a trace was asked for and named nothing to follow."
        ),
        "READ-5": ListedRefusal(
            "NOT_A_SEASON", 400, "Raised where the season to narrow a trace to is not a number."
        ),
        "READ-6": ListedRefusal("NO_SETTING", 400, "Raised where a setting was asked for by an empty name."),
        "READ-7": ListedRefusal(
            "NO_MEMBER", 400, "Raised where a household member was asked for by an empty name."
        ),
        "READ-8": ListedRefusal(
            "NO_SHELF_WITHOUT_A_MEMBER",
            400,
            "Raised where a shelf was asked for and nobody was named whose it is.",
        ),
        "READ-9": ListedRefusal(
            "NOT_A_COUNT", 400, "Raised where how many holdings to answer with is not a whole number."
        ),
        "REPAIR-1": ListedRefusal(
            "STALE", 400, "Raised when consent was given for an offer that no longer stands."
        ),
        "RESTORE-11": ListedRefusal(
            "MOVED_ON", 400, "Raised when consent was given for a listing that no longer stands."
        ),
        "SERVE-6": ListedRefusal("UNRENDERABLE", 500, "Raised when an answer could not be rendered."),
        "SERVE-7": ListedRefusal(
            "NO_JOB_NAME", 500, "Raised when this machine will not supply the randomness a job is named with."
        ),
        "SERVE-8": ListedRefusal(
            "UNANSWERED", 500, "Raised when an action's work ended before it had an answer to give."
        ),
        "SPACE-6": ListedRefusal(
            "ANOTHER_OFFER", 400, "Raised when an agreement names an offer that is not the one standing now."
        ),
        "STACK-1": ListedRefusal(
            "STACK_UNREADABLE", 500, "Raised when a stack directory holds no readable manifest."
        ),
        "STACK-10": ListedRefusal(
            "STACK_UNASSEMBLED", 500, "Raised when a manifest's files are not laid out as the contract says."
        ),
        "STACK-2": ListedRefusal(
            "STACK_UNUSABLE", 500, "Raised when a manifest is readable and this build cannot use it."
        ),
        "STACK-3": ListedRefusal("STACK_NOT_EMBEDDED", 500, "Raised when the embedded stack is not intact."),
        "STACK-4": ListedRefusal(
            "STACK_NOT_SET_UP", 500, "Raised when lemonfiber has nowhere to write the stack."
        ),
        "STACK-5": ListedRefusal(
            "STACK_NOT_WRITTEN", 500, "Raised when the stack could not be written to disk."
        ),
        "STACK-6": ListedRefusal(
            "STACK_INVALID", 500, "Raised when a manifest parses and breaks the contract."
        ),
        "STACK-7": ListedRefusal("STACK_MALFORMED", 500, "Raised when a manifest is not TOML at all."),
        "STACK-8": ListedRefusal(
            "STACK_UNRECOGNISED", 500, "Raised when a manifest declares names this build does not know."
        ),
        "STACK-9": ListedRefusal(
            "STACK_NEEDS_NEWER", 500, "Raised when a stack names a newer lemonfiber than the one running."
        ),
        "UPDATE-5": ListedRefusal(
            "UPDATE_MOVED",
            400,
            "Raised where an update names an offer that is not the one a fresh look at the releases builds.",
        ),
        "WIRE-1": ListedRefusal(
            "NO_SUCH_FILLER", 404, "A capability was named that no service in this stack provides."
        ),
        "WIRE-2": ListedRefusal(
            "CANNOT_FILL", 400, "The service named cannot do the thing it was asked to fill."
        ),
        "WIRE-3": ListedRefusal(
            "NOTHING_ASKS",
            400,
            "Nothing in this stack asks for the capability, so a choice would change nothing.",
        ),
        "WIRE-4": ListedRefusal(
            "CHOICE_UNWRITABLE", 500, "The setting recording the choice could not be written."
        ),
        "WIRE-5": ListedRefusal(
            "WIRING_MOVED",
            400,
            "Raised when a choice answers an offer that was read against a wiring that has since moved.",
        ),
        "WIRE-6": ListedRefusal(
            "UNREASONABLE",
            400,
            "Raised when the reason given for a choice is longer than a reason may be, or holds a line break or another control character.",
        ),
        "WIRE-7": ListedRefusal(
            "ALREADY_FILLS",
            400,
            "Raised where the service chosen already fills the capability, so there is nothing to change.",
        ),
    }
)
"""What the contract says of each refusal code."""


def is_refusal_code(value: str) -> typing.TypeIs[RefusalCode]:
    """Tell whether a code is one the contract lists as a refusal's."""
    return value in REFUSAL_CODES


__all__ = [
    "ListedRefusal",
    "REFUSAL_CODES",
    "RefusalCode",
    "is_refusal_code",
]
