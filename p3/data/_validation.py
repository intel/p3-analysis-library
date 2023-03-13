# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import json
import jsonschema

_coverage_schema_id = (
    "https://raw.githubusercontent.com/intel/"
    "p3-analysis-library/p3/schema/coverage-0.1.0.schema"
)
_coverage_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": _coverage_schema_id,
    "title": "Coverage",
    "description": "Lines of code used in each file of a code base.",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "file": {"type": "string"},
            "regions": {
                "type": "array",
                "items": {
                    "type": "array",
                    "prefixItems": [
                        {"type": "integer"},
                        {"type": "integer"},
                        {"type": "integer"},
                    ],
                    "items": False,
                },
            },
        },
        "required": ["file", "regions"],
    },
}


def _validate_coverage_json(json_string: str) -> object:
    """
    Validate coverage JSON string against schema.

    Parameters
    ----------
    json_string : String
        The JSON string to validate.

    Returns
    -------
    Object
        A Python object corresponding to the JSON string.

    Raises
    ------
    ValueError
        If the JSON string fails to validate.

    TypeError
        If the JSON string is not a string.
    """
    if not isinstance(json_string, str):
        raise TypeError("Coverage must be a JSON string.")

    instance = json.loads(json_string)

    try:
        jsonschema.validate(instance=instance, schema=_coverage_schema)
    except Exception:
        msg = "Coverage string failed schema validation"
        raise ValueError(msg)

    return instance
