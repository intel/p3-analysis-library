# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

# This file incorporates work covered by the following copyright and permission
# notice:
# Copyright (c) 2020 Performance Portability authors
# SPDX-License-Identifier: MIT

from p3._utils import _require_columns


def cascade(df, eff=None, size=None, **kwargs):
    """
    Plot a `cascade`_ summarizing the efficiency and performance
    portability of each application in a DataFrame, highlighting
    differences in platform support across the applications.

    .. _cascade: https://doi.org/10.1109/P3HPC51967.2020.00007

    Parameters
    ----------
    df: DataFrame
        A pandas DataFrame storing performance efficiency data.
        The following columns are always required: "problem", "platform",
        "application". At least one of the following columns is required:
        "app eff" or "arch eff".

    eff: string, optional
        The efficiency value to use when plotting the cascade. Must be either
        "app" or "arch". If no value is provided, the efficiency is selected
        automatically based on the data available in `df`.

    size: 2-tuple of floats, optional
        The size of the plot, in backend-specific units.
        In the matplotlib backend, the default is (6, 5), in the pgfplots
        backend the size controls only the top left plot, where the default
        is ("200pt", "200pt")

    **kwargs: properties, optional
        `kwargs` are used to specify properties that control various styling
        options (e.g. colors and markers).

        .. list-table:: Properties
            :widths: 10, 20, 18
            :header-rows: 1

            * - Property
              - Type
              - Description

            * - `platform_legend`
              - p3.plot.Legend
              - Styling options for platform legend.

            * - `application_legend`
              - p3.plot.Legend
              - Styling options for application legend.

            * - `platform_style`
              - p3.plot.PlatformStyle
              - Styling options for platforms.

            * - `application_style`
              - p3.plot.ApplicationStyle
              - Styling options for applications.

    Returns
    -------
    ~p3.plot.backend.CascadePlot
        An object providing direct access to backend-specific components
        of the cascade plot.

    Raises
    ------
    ValueError
        If any of the required columns are missing from `df`.
        If `eff` is set to any value other than "app" or "arch".

    TypeError
        If any of the values in the efficiency column(s) is non-numeric.
    """
    _require_columns(df, ["problem", "platform", "application"])

    if len(df["problem"].unique()) > 1:
        raise NotImplementedError(
            "Handling multiple problems is currently not implemented.",
        )

    kwargs.setdefault("backend", "matplotlib")
    backend = kwargs["backend"]
    if backend == "matplotlib":
        from p3.plot.backend.matplotlib import CascadePlot

        return CascadePlot(df, eff, size, **kwargs)
    elif backend == "pgfplots":
        from p3.plot.backend.pgfplots import CascadePlot

        return CascadePlot(df, eff, size, **kwargs)
    else:
        raise ValueError(
            "'backend' must be one of the supported backends: ",
            "'matplotlib', 'pgfplots'",
        )
