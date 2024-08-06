import json
import jsonschema
import os

def _validate_coverage_data(coverage_data) -> object:
    """
    Validate coverage data (either JSON string or object) against schema.

    Parameters
    ----------
    coverage_data : String or Object
        The JSON string or object to validate.

    Returns
    -------
    Object
        A Python object corresponding to the JSON data.

    Raises
    ------
    ValueError
        If the data fails to validate.

    TypeError
        If the data is not a string or dictionary.
    """
    if isinstance(coverage_data, str):
        instance = json.loads(coverage_data)
    elif isinstance(coverage_data, dict):
        instance = coverage_data
    else:
        raise TypeError("Coverage must be a JSON string or dictionary.")

    schema_path = os.path.join(os.path.dirname(__file__), "coverage-0.3.0.schema")
    if not os.path.exists(schema_path):
        msg = "Could not locate coverage schema file"
        raise RuntimeError(msg)

    with open(schema_path, 'r') as schema_file:
        schema = json.load(schema_file)

    try:
        jsonschema.validate(instance=instance, schema=schema)
    except jsonschema.exceptions.ValidationError:
        msg = "Coverage data failed schema validation"
        raise ValueError(msg)
    except jsonschema.exceptions.SchemaError:
        msg = "coverage-0.3.0.schema is not a valid schema"
        raise RuntimeError(msg)

    return instance
