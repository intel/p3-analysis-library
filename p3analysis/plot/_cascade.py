# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

# This file incorporates work covered by the following copyright and permission
# notice:
# Copyright (c) 2020 Performance Portability authors
# SPDX-License-Identifier: MIT

import copy

from p3analysis._utils import _cast_to_numeric, _require_columns


def cascade(
    df,
    eff=None,
    *,
    size=None,
    platform_legend=None,
    application_legend=None,
    platform_style=None,
    application_style=None,
    backend="matplotlib",
    **kwargs,
):
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

    platform_legend: p3analysis.plot.Legend, optional
        Styling options for platform legend.

    application_legend: p3analysis.plot.Legend, optional
        Styling options for application legend.

    platform_style: p3analysis.plot.PlatformStyle, optional
        Styling options for platforms.

    application_style: p3analysis.plot.ApplicationStyle, optional
        Styling options for applications.

    backend: str, {"matplotlib", "pgfplots"}, default: "matplotlib"
        Backend to use to produce the plot.

    **kwargs: properties, optional
        `kwargs` are used to specify properties that control various
        backend-specific plotting options.

    Returns
    -------
    ~p3analysis.plot.backend.CascadePlot
        An object providing direct access to backend-specific components
        of the cascade plot.

    Raises
    ------
    ValueError
        If any of the required columns are missing from `df`.
        If `eff` is set to any value other than "app" or "arch".
        If any (application, platform) pair has multiple efficiency values,
        since the plot shows only one efficiency value per (application,
        platform) combination.

    TypeError
        If any of the values in the efficiency column(s) is non-numeric.
    """
    _require_columns(df, ["problem", "platform", "application"])

    if len(df["problem"].unique()) > 1:
        raise NotImplementedError(
            "Handling multiple problems is currently not implemented.",
        )

    # Choose efficiency column based on eff parameter and available columns
    efficiency_columns = []

    for column in ["app eff", "arch eff"]:
        if column in df:
            efficiency_columns.append(column)
    if len(efficiency_columns) == 0:
        msg = (
            "DataFrame does not contain an 'app eff' or 'arch eff' ",
            "column.",
        )
        raise ValueError(msg)

    if eff is None:
        eff_column = efficiency_columns[0]
    else:
        if eff not in ["app", "arch"]:
            raise ValueError("'eff' must be 'app' or 'arch'.")
        eff_column = eff + " eff"
        if eff_column not in df:
            msg = "DataFrame does not contain an '%s' column."
            raise ValueError(msg % (eff_column))
    df = _cast_to_numeric(df, [eff_column])

    # Check there is only one entry per (application, platform) pair.
    grouped = df.groupby(["platform", "application"])
    if not (grouped[eff_column].nunique() == 1).all():
        raise ValueError(
            "Each (application, platform) pair must be associated with "
            + "exactly one efficiency value.",
        )

    # Add styling options, if provided, into kwargs.
    # Permits different backends to set different defaults.
    kwargs = copy.deepcopy(kwargs)
    if platform_legend:
        kwargs["platform_legend"] = platform_legend
    if application_legend:
        kwargs["application_legend"] = application_legend
    if platform_style:
        kwargs["platform_style"] = platform_style
    if application_style:
        kwargs["application_style"] = application_style

    if backend == "matplotlib":
        from p3analysis.plot.backend.matplotlib import CascadePlot

        return CascadePlot(df, eff_column, size, **kwargs)
    elif backend == "pgfplots":
        from p3analysis.plot.backend.pgfplots import CascadePlot

        return CascadePlot(df, eff_column, size, **kwargs)
    else:
        raise ValueError(
            "'backend' must be one of the supported backends: ",
            "'matplotlib', 'pgfplots'",
        )
