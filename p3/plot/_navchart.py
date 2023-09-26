# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
import numpy as np
import pandas as pd

from p3._utils import _require_columns, _require_numeric
from p3.plot._cascade import _get_colors
from p3.plot.backend.matplotlib import NavChart


def navchart(pp, cd, eff=None, goal=None, **kwargs):
    """
    Plot a `navigation chart`_ showing the performance portability and code
    convergence of each application in a DataFrame. The chart highlights the
    tradeoff between performance (portability) and programmer productivity,
    assisting in navigation of the P3 space and reasoning about how to reach
    development goals.

    The chart is plotted using the current pyplot figure, if one exists.

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

            * - `app_cmap`
              - Colormap, string, or list
              - Colormap for applications

            * - `app_markers`
              - list
              - Markers for applications

        .. list-table:: matplotlib Properties
            :widths: 10, 20, 18
            :header-rows: 1

            * - Property
              - Type
              - Description

            * - `legend_kwargs`
              - dict
              - `kwargs` passed to legend

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
            "Handling multiple problems is currently not implemented."
        )

    kwargs.setdefault("app_cmap", getattr(plt.cm, "tab10"))

    default_markers = getattr(matplotlib.markers.MarkerStyle, "filled_markers")
    kwargs.setdefault("app_markers", default_markers)

    kwargs.setdefault("legend_kwargs", {})
    kwargs["legend_kwargs"].setdefault("loc", "upper center")
    kwargs["legend_kwargs"].setdefault("bbox_to_anchor", (0.5, 0.0))

    # Choose the PP column based on eff parameter and available columns
    pp_columns = []
    for column in ["app pp", "arch pp"]:
        if column in pp:
            pp_columns.append(column)
    if len(pp_columns) == 0:
        msg = "DataFrame does not contain an 'app pp' or 'arch pp' column."
        raise ValueError(msg)

    if eff is None:
        pp_column = pp_columns[0]
    else:
        if eff not in ["app", "arch"]:
            raise ValueError("'eff' must be 'app' or 'arch'.")
        pp_column = eff + " eff"
        if pp_column not in pp:
            msg = "DataFrame does not contain an '%s' column."
            raise ValueError(msg % (pp_column))
    _require_numeric(pp, [pp_column])

    ppcd = pd.merge(pp, cd, on=["problem", "application"], how="inner")

    applications = ppcd["application"].unique()
    app_colors = _get_colors(applications, kwargs["app_cmap"])

    markers = kwargs["app_markers"]
    if not isinstance(markers, (list, tuple)):
        raise ValueError("Unsupported type provided for app_markers")
    app_markers = {app: marker for app, marker in zip(applications, markers)}

    # Add a small amount of jitter to make overlapping points less likely
    jitter = np.random.default_rng().uniform(0, 0.01, 2 * len(ppcd))

    fig = plt.gcf()
    ax = plt.gca()
    patch_size = 0.1
    for index, row in ppcd.iterrows():
        app_name = row["application"]
        app_pp = row[pp_column]
        convergence = 1 - row["divergence"]
        jitter_x = jitter[2 * index + 0]
        jitter_y = jitter[2 * index + 1]
        patch_x = convergence - patch_size / 2 + jitter_x
        patch_y = app_pp - patch_size / 2 + jitter_y
        patch = mpatches.Rectangle(
            (patch_x, patch_y),
            0.1,
            0.1,
            linewidth=1,
            edgecolor=app_colors[app_name],
            fill=False,
            clip_on=False,
        )
        ax.add_patch(patch)
        ax.plot(
            convergence + jitter_x,
            app_pp + jitter_y,
            color=app_colors[app_name],
            label=app_name,
            clip_on=False,
            marker=app_markers[app_name],
            markersize=8,
            zorder=10,
        )
    ax.grid(True)

    # Goal Region
    if goal and goal != (1, 1):
        port_min = goal[0]
        conv_min = goal[1]
        verts = [
            (conv_min, port_min),  # left, bottom
            (conv_min, 1.0),  # left, top
            (1.0, 1.0),  # right, top
            (1.0, port_min),  # right, bottom
            (0.0, 0.0),  # ignored
        ]

        codes = [
            Path.MOVETO,
            Path.LINETO,
            Path.LINETO,
            Path.LINETO,
            Path.CLOSEPOLY,
        ]
        path = Path(verts, codes)
        patch = mpatches.PathPatch(path, facecolor="yellow", lw=2, alpha=0.5)
        ax.add_patch(patch)

        # Goal Lines
        plt.axhline(y=port_min, lw=2, color="blue", ls="--")
        plt.axvline(x=conv_min, lw=2, color="blue", ls="--")

    # Unportable line
    plt.axhline(alpha=0.3, lw=10, color="red", clip_on=False)
    plt.text(0.5, 0.004, "Unportable", ha="center")

    # Right top arrow - Abstraction
    plt.arrow(
        0.5,
        1.05,
        0.5,
        0,
        width=0.04,
        head_length=0.05,
        head_width=0.08,
        clip_on=False,
        color="blue",
        length_includes_head=True,
        shape="full",
        alpha=0.5,
    )
    plt.text(0.75, 1.04, "Abstraction", ha="center")

    # left top arrow - Specialization
    plt.arrow(
        0.5,
        1.05,
        -0.5,
        0,
        width=0.04,
        head_length=0.05,
        head_width=0.08,
        clip_on=False,
        color="purple",
        length_includes_head=True,
        alpha=0.5,
    )
    plt.text(0.25, 1.04, "Specialization", ha="center")

    # Vertical Arrow - Optimization
    plt.arrow(
        1.05,
        0.5,
        0,
        0.5,
        width=0.04,
        head_length=0.05,
        head_width=0.08,
        clip_on=False,
        color="green",
        length_includes_head=True,
        alpha=0.5,
    )
    plt.text(
        1.03,
        0.75,
        "Optimization",
        rotation="vertical",
        va="center",
    )

    # Vertical Arrow - Regression
    plt.arrow(
        1.05,
        0.5,
        0,
        -0.5,
        width=0.04,
        head_length=0.05,
        head_width=0.08,
        clip_on=False,
        color="pink",
        length_includes_head=True,
        alpha=0.5,
    )
    plt.text(
        1.03,
        0.25,
        "Regression",
        rotation="vertical",
        va="center",
    )

    if pp_column == "app pp":
        ax.set_ylabel("Performance Portability (App. Eff.)")
    elif pp_column == "arch pp":
        ax.set_ylabel("Performance Portability (Arch. Eff.)")
    ax.set_xlabel("Code Convergence")
    ax.set_ylim([0, 1])
    ax.set_xlim([0, 1])

    fig.legend(**kwargs["legend_kwargs"])

    return NavChart(fig, ax)
