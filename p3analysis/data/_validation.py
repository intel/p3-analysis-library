# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import json
import pkgutil
from typing import Any

import jsonschema


def _validate_coverage_json(json_data: Any) -> object:
    """
    Validate coverage JSON against schema.

    Parameters
    ----------
    json_data : Any
        The JSON string or object to validate.

    Returns
    -------
    Object
        A Python object corresponding to the JSON provided.

    Raises
    ------
    ValueError
        If the JSON fails to validate.
    """
    if isinstance(json_data, str):
        instance = json.loads(json_data)
    else:
        instance = json_data

    schema_string = pkgutil.get_data(__name__, "coverage.schema")
    if not schema_string:
        msg = "Could not locate coverage schema file"
        raise RuntimeError(msg)

    schema = json.loads(schema_string)

    try:
        jsonschema.validate(instance=instance, schema=schema)
    except jsonschema.exceptions.ValidationError:
        msg = "Coverage data failed schema validation"
        raise ValueError(msg)
    except jsonschema.exceptions.SchemaError:
        msg = "coverage.schema is not a valid schema"
        raise RuntimeError(msg)

    return instance
