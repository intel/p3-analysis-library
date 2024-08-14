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


def _require_numeric(df, columns):
    """
    Check that the named columns are numeric.
    """

    for column in columns:
        try:
            pd.to_numeric(df[column])
        except Exception:
            msg = "Column '%s' must contain only numeric values."
            raise TypeError(msg % (column))


def _sort_by_app_order(df, app_order):
    """
    Sort the DataFrame such that the order of applications matches that
    specified in app_order.
    """

    def index_function(row):
        return app_order.tolist().index(row["application"])

    sort_index = df.apply(index_function, axis=1)
    sort_index.name = "sort_index"

    order = df.join(sort_index).sort_values(by=["sort_index"]).index
    df = df.loc[order]
    df.reset_index(inplace=True, drop=True)  # add style change
    return df
