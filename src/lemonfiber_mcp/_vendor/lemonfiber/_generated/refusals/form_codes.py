# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `FORM` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

FORM: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "FORM-1": ListedRefusal("NO_FORM_NAMED", 400, "Raised when no form was named."),
    "FORM-2": ListedRefusal("NO_SUCH_FORM", 404, "Raised when a named form is not declared by the stack."),
    "FORM-3": ListedRefusal(
        "FORMS_CONFLICT", 400, "Raised when forms that cannot be combined are named together."
    ),
}
"""What the contract says of each `FORM` code."""
