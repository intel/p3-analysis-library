# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import pandas as pd
from itertools import product

from statistics import harmonic_mean

from p3._utils import _require_columns, _require_numeric


def pp(df):
    r"""
    Calculate performance portability from architectural and/or application
    efficiency.

    Performance portability is calculated as proposed by Pennycook, Sewall and
    Lee in "`A Metric for Performance Portability`_". For a given set of
    platforms, :math:`H`, the performance portability :math:`PP` of an
    application :math:`a` solving problem :math:`p` is:

    .. math::
        PP(a, p, H) = \cases{
          \dfrac{|H|}{\sum_{i \in H} \dfrac{1}{e_i(a,p)}} &
            $\text{if } i \text{ is supported } \forall i \in H$ \cr
          0 &
            $\text{ otherwise }$
        }

    where :math:`e_i(a,p)` is the performance efficiency of application
    :math:`a` solving problem :math:`p` on platform :math:`i`.

    .. _A Metric for Performance Portability:
        https://doi.org/10.48550/arXiv.1611.07409

    Parameters
    ----------
    df: DataFrame
        A pandas DataFrame storing performance data. The following columns are
        always required: "problem", "platform", "application". At least one of
        the following two columns are required: "arch eff", "app eff".

    Returns
    -------
    DataFrame
        A new pandas DataFrame storing the performance portability values
        calculated from the architectural efficiency and/or application
        efficiency data provided in `df`.

    Raises
    ------
    ValueError
        If any of the required columns are missing from `df`.

    TypeError
        If any of the values in the efficiency column(s) are non-numeric.
    """
    _require_columns(df, ["problem", "platform", "application"])

    # We need at least one efficiency
    efficiencies = []
    if "app eff" in df:
        efficiencies.append("app eff")
    if "arch eff" in df:
        efficiencies.append("arch eff")
    if len(efficiencies) == 0:
        msg = "DataFrame must contain a column named 'arch eff' or 'app eff'."
        raise ValueError(msg)
    _require_numeric(df, efficiencies)

    # Check that efficiencies are not given in percentages
    for eff in efficiencies:
        if not df[eff].fillna(0).between(0, 1).all():
            raise ValueError("%s must in range [0, 1]" % eff)

    # Add a "did not run" value for applications that did not run
    rows = []
    combination_keys = ["problem", "platform", "application"]
    unique = [df[key].unique() for key in combination_keys]
    for combination in product(*unique):
        problem, platform, application = combination
        sliced = df.loc[
            (df["problem"] == problem)
            & (df["platform"] == platform)
            & (df["application"] == application)
        ]
        if sliced.empty:
            rows += [
                {
                    "problem": problem,
                    "platform": platform,
                    "application": application,
                    "fom": None,
                    "arch eff": None,
                    "app eff": None,
                }
            ]
    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)

    # Calculate performance portability for both types of efficiency
    key = ["problem", "application"]
    groups = df[key + efficiencies].fillna(0.0).groupby(key)
    pp = groups.agg(harmonic_mean)
    pp.reset_index(inplace=True)
    for eff in efficiencies:
        new_column = eff.replace("eff", "pp")
        pp.rename(columns={eff: new_column}, inplace=True)
        pp = pp.astype({new_column: "float64"})

    return pp
