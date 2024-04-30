# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

from p3._utils import _require_columns, _require_numeric


def navchart(pp, cd, eff=None, size=None, goal=None, **kwargs):
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

    **kwargs: properties, optional
        `kwargs` are used to specify properties that control various styling
        options (e.g. colors and markers).

        .. list-table:: Properties
            :widths: 10, 20, 18
            :header-rows: 1

            * - Property
              - Type
              - Description

            * - `legend`
              - p3.plot.Legend
              - Styling options for platform legend.

            * - `style`
              - p3.plot.ApplicationStyle
              - Styling options for applications.

    Returns
    -------
    ~p3.plot.backend.NavChart
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

    kwargs.setdefault("backend", "matplotlib")
    backend = kwargs["backend"]
    if backend == "matplotlib":
        from p3.plot.backend.matplotlib import NavChart

        return NavChart(pp, cd, eff, size, goal, **kwargs)
    elif backend == "pgfplots":
        from p3.plot.backend.pgfplots import NavChart

        return NavChart(pp, cd, eff, size, goal, **kwargs)
    else:
        raise ValueError(
            "'backend' must be one of the supported backends: ",
            "'matplotlib', 'pgfplots'",
        )
