# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import pandas as pd


def _require_columns(df, columns):
    """
    Check that the DataFrame has the expected column names.
    Exit if any of the columns are missing.
    """

    for column in columns:
        if column not in df:
            msg = (
                "DataFrame does not contain a column named '%s'. "
                "The following columns are required: %s"
            )
            raise ValueError(msg % (column, str(columns)))


def _cast_to_numeric(df, columns):
    """
    Check that the named columns are numeric, and cast them.
    """
    _require_columns(df, columns)
    result = df.copy(deep=True)
    for column in columns:
        try:
            result[column] = pd.to_numeric(df[column])
        except Exception:
            msg = "Column '%s' must contain only numeric values."
            raise TypeError(msg % (column))
    return result
