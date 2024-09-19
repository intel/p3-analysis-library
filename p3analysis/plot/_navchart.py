# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import copy

from p3analysis._utils import _require_columns, _require_numeric


def navchart(
    pp,
    cd,
    eff=None,
    *,
    size=None,
    goal=None,
    legend=None,
    style=None,
    backend="matplotlib",
    **kwargs,
):
    """
    Plot a `navigation chart`_ showing the performance portability and code
    convergence of each application in a DataFrame. The chart highlights the
    tradeoff between performance (portability) and programmer productivity,
    assisting in navigation of the P3 space and reasoning about how to reach
    development goals.

    .. _navigation chart: https://doi.org/10.1109/MCSE.2021.3097276

    Parameters
    ----------
    pp: DataFrame
        A pandas DataFrame storing performance portability data.
        The following columns are always required: "problem", "application".
        At least one of the following columns is required: "app pp" or "arch
        pp".

    cd: DataFrame
        A pandas DataFrame storing code divergence data.
        The following columns are required: "problem", "application",
        "divergence".

    eff: string, optional
        The efficiency value to use when plotting the navchart. Must be either
        "app" or "arch". If no value is provided, the efficiency is selected
        automatically based on the data available in `pp`.

    size: 2-tuple of floats, optional
        The size of the plot, in backend-specific units.
        In the matplotlib backend, the default is (5, 5), in the pgfplots
        backend, the default is ("200pt", "200pt")

    goal: tuple, optional
        User-defined goal, expressed as (convergence, portability).
        The region between this point and (1, 1) will be highlighted.

    legend: p3analysis.plot.Legend, optional
        Styling options for platform legend.

    style: p3analysis.plot.ApplicationStyle, optional
        Styling options for applications.

    backend: str, {"matplotlib", "pgfplots"}, default: "matplotlib"
        Backend to use to produce the plot.

    **kwargs: properties, optional
        `kwargs` are used to specify properties that control various
        backend-specific plotting options.

    Returns
    -------
    ~p3analysis.plot.backend.NavChart
        An object providing direct access to backend-specific components
        of the navigation chart.

    Raises
    ------
    ValueError
        If any of the required columns are missing from `pp` or `cd`.
        If `eff` is set to any value other than "app" or "arch".

    TypeError
        If any of the values in the "pp" column(s) of `pp` or the
        "divergence" column of `cd` are non-numeric.
    """

    _require_columns(pp, ["problem", "application"])
    _require_columns(cd, ["problem", "application", "divergence"])
    _require_numeric(cd, ["divergence"])

    if len(cd["problem"].unique()) > 1:
        raise NotImplementedError(
            "Handling multiple problems is currently not implemented.",
        )

    # Add styling options, if provided, into kwargs.
    # Permits different backends to set different defaults.
    kwargs = copy.deepcopy(kwargs)
    if legend:
        kwargs["legend"] = legend
    if style:
        kwargs["style"] = style

    if backend == "matplotlib":
        from p3analysis.plot.backend.matplotlib import NavChart

        return NavChart(pp, cd, eff, size, goal, **kwargs)
    elif backend == "pgfplots":
        from p3analysis.plot.backend.pgfplots import NavChart

        return NavChart(pp, cd, eff, size, goal, **kwargs)
    else:
        raise ValueError(
            "'backend' must be one of the supported backends: ",
            "'matplotlib', 'pgfplots'",
        )
