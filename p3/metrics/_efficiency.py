# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import numpy

from p3._utils import _require_columns, _require_numeric


def application_efficiency(df, foms="lower"):
    """
    Calculate application efficiency.

    Application efficiency represents achieved performance relative to the
    best-known performance of any other application solving the same problem
    on the same platform. This function determines the "best-known" performance
    for each combination of "platform" and "problem" in the input DataFrame.

    Calculated values will lie in the range :math:`[0, 1]`.

    Parameters
    ----------
    df: DataFrame
        A pandas DataFrame storing performance data. The following columns are
        required: "problem", "platform", "application", "fom".

    foms: string
        The interpretation of the figure of merit: "lower" if lower values are
        better, and "higher" if higher values are better.

    Returns
    -------
    DataFrame
        A new pandas DataFrame storing the application efficiency values
        calculated from the performance data
        provided in `df`.

    Raises
    ------
    ValueError
        If any of the required columns are missing from `df`.
        If `foms` is not "lower" or "higher".

    TypeError
        If any value in the "fom" column of `df` is a non-numeric value.
    """
    required_columns = ["problem", "platform", "application", "fom"]
    _require_columns(df, required_columns)
    _require_numeric(df, ["fom"])

    if foms not in ["lower", "higher"]:
        raise ValueError("FOM interpretation must be 'lower' or 'higher'")

    result = df.filter(required_columns)

    # Identify the best FOM for each (problem, platform) triple
    key = ["problem", "platform"]
    groups = df[key + ["fom"]].groupby(key)
    best = groups.agg("min") if foms == "lower" else groups.agg("max")
    best.reset_index(inplace=True)

    # Calculate application efficiency
    def app_eff(row):
        value = [row["problem"], row["platform"]]
        fom = float(row["fom"])
        best_fom = float(best.loc[(best[key] == value).all(1)]["fom"])
        if foms == "lower":
            return 0.0 if numpy.isnan(fom) else (best_fom / fom)
        else:
            return fom / best_fom

    result["app eff"] = result.apply(app_eff, axis=1)

    return result
