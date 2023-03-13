# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

from p3._utils import _require_columns


def _collapse(df, columns, name):
    """
    Combine the specified columns into one with the new name, and remove the
    old columns.
    """
    if len(columns) > 1:
        df[name] = df[columns].agg("-".join, axis=1)
        df.drop(columns=columns, inplace=True)
    elif len(columns) == 1:
        df.rename(columns={columns[0]: name}, inplace=True)


def projection(
    df, problem=["problem"], application=["application"], platform=["platform"]
):
    """
    Project data onto definitions of problem, application and platform.

    The result of a projection is a DataFrame suitable for use with
    functionality provided by the :py:mod:`p3.metrics`, :py:mod:`p3.plot` and
    :py:mod:`p3.report` modules.

    Parameters
    ----------
    df : DataFrame
        A pandas DataFrame storing raw performance data.

    problem,application,platform : list,optional
        A list of column names in `df` that define the required projection.

        Values from the columns specified in each of these lists will be
        concatenated to form new "problem", "application" and "platform"
        columns. If no column names are provided, columns named "problem",
        "application" and "platform" are assumed to already exist.

    Returns
    -------
    DataFrame
        A new pandas DataFrame storing the projected data.

    Raises
    ------
    ValueError
        If any of the column names provided in `problem`, `application` or
        `platform` are missing from `df`.

    TypeError
        If `problem`, `application` or `platform` are not lists of strings.

    Examples
    --------
    >>> df = pd.DataFrame({'fom': [1.0, 2.0],
    ...                    'language': ['OpenMP', 'OpenMP'],
    ...                    'branch': ['master', 'optimized'],
    ...                    'architecture': ['CPU', 'CPU'],
    ...                    'compiler': ['gcc', 'icc'],
    ...                    'kernel': ['DGEMM', 'DGEMM'],
    ...                    'M': ['1024', '1024'],
    ...                    'N': ['1024', '1024'],
    ...                    'K': ['1024', '1024']})
    >>> df = p3.data.projection(df,
    ...                         problem=['kernel', 'M', 'N', 'K'],
    ...                         application=['language', 'branch'],
    ...                         platform=['architecture', 'compiler'])
    >>> df
       fom               problem       application platform
    0  1.0  DGEMM-1024-1024-1024     OpenMP-master  CPU-gcc
    1  2.0  DGEMM-1024-1024-1024  OpenMP-optimized  CPU-icc
    """
    for definition in [problem, application, platform]:
        if not isinstance(definition, list):
            raise TypeError("Projection definition must be a list.")
        for column in definition:
            if not isinstance(column, str):
                raise TypeError("Column name(s) must be a string.")

    definitions = problem + application + platform
    _require_columns(df, definitions)

    # Columns in definition(s) become part of the name, so must be strings
    result = df.astype({col: "str" for col in definitions})

    # Create new columns for problem, application and platform
    _collapse(result, problem, "problem")
    _collapse(result, application, "application")
    _collapse(result, platform, "platform")

    return result
