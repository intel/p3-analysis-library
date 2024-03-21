# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import json
import jsonschema
import pkgutil


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

    schema_string = pkgutil.get_data(__name__, "coverage-0.3.0.schema")
    if not schema_string:
        msg = "Could not locate coverage schema file"
        raise RuntimeError(msg)

    schema = json.loads(schema_string)

    try:
        jsonschema.validate(instance=instance, schema=schema)
    except jsonschema.exceptions.ValidationError:
        msg = "Coverage string failed schema validation"
        raise ValueError(msg)
    except jsonschema.exceptions.SchemaError:
        msg = "coverage-0.3.0.schema is not a valid schema"
        raise RuntimeError(msg)

    return instance
