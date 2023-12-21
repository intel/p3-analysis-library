# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

# This file incorporates work covered by the following copyright and permission
# notice:
# Copyright (c) 2020 Performance Portability authors
# SPDX-License-Identifier: MIT

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import p3.metrics
import string
import jinja2
import os

from p3._utils import _require_columns, _require_numeric
from p3.plot._common import Legend, ApplicationStyle, PlatformStyle
from p3.plot.backend.matplotlib import CascadePlot as MPLCascadePlot
from p3.plot.backend.pgfplots import CascadePlot as PGFCascadePlot


class _PlatformLegendHandler(matplotlib.legend_handler.HandlerBase):
    def __init__(self, colors, labels):
        self.colors = colors
        self.labels = labels
        super().__init__()

    def create_artists(
        self,
        legend,
        orig_handle,
        xdescent,
        ydescent,
        width,
        height,
        fontsize,
        trans,
    ):
        artist = []

        # Draw a box using the platform's assigned color
        name = orig_handle.get_label()
        color = self.colors[name]
        rect = mpatches.Rectangle(
            [xdescent, ydescent - height / 2],
            width,
            height * 2,
            facecolor=color,
            edgecolor="black",
            lw=1,
        )
        artist.append(rect)

        # Draw text in the box using the platform's assigned label
        txt = matplotlib.text.Text(
            xdescent + width * 0.5,
            ydescent + height * 0.4,
            self.labels[name],
            ha="center",
            va="center",
            c="black",
            fontsize=fontsize,
            fontfamily="sans-serif",
            zorder=4,
        )
        artist.append(txt)

        return artist


def _efficiency_cascade(ax, df, eff_column, colors, markers):
    """
    Plot the efficiency cascade using the axes provided.
    """
    platforms = df["platform"].unique()
    applications = df["application"].unique()

    ax.set_xticks(np.arange(1, len(platforms) + 1))
    if eff_column == "app eff":
        ax.set_ylabel("Application Efficiency")
    elif eff_column == "arch eff":
        ax.set_ylabel("Architectural Efficiency")
    else:
        msg = "Unexpected efficiency column name: %s"
        raise ValueError(msg % (eff_column))
    ax.set_ylim([0, 1.1])
    ax.grid(visible=True)

    handles = []
    for app_name in applications:
        app_df = df[(df["application"] == app_name) & (df[eff_column] > 0.0)]
        app_df = app_df.sort_values(by=[eff_column], ascending=False)

        supported_platforms = list(app_df["platform"])
        xvalues = np.arange(1, len(supported_platforms) + 1)

        handle = ax.plot(
            xvalues,
            app_df[eff_column],
            label=app_name,
            color=colors[app_name],
            marker=markers[app_name],
            markersize=8,
            lw=1.5,
        )

        handles += handle

    return handles


def _platform_chart(
    ax, df, eff_column, app_colors, app_markers, plat_colors, plat_labels
):
    """
    Plot the platform chart using the axes provided
    """
    platforms = df["platform"].unique()
    applications = df["application"].unique()

    ax.set_xlabel("Platform")
    ax.set_yticks([])
    ax.set_ylim([0, len(platforms)])

    # Size boxes to fill the height of the platform chart
    fac = len(platforms) / len(applications)

    # Leave space either side of the boxes for the markers
    ax.set_xlim([-0.5, len(platforms) + 1.5])

    # Plot the applications in reverse, because ax.bar plots bottom-up
    for i, app_name in enumerate(reversed(applications)):
        app_df = df[(df["application"] == app_name) & (df[eff_column] > 0.0)]
        app_df = app_df.sort_values(by=[eff_column], ascending=False)

        # Draw a line behind the boxes to represent the application
        endpoints = [0, len(platforms) + 1]
        ax.plot(
            endpoints,
            len(endpoints) * [(i + 0.5) * fac],
            color=app_colors[app_name],
            marker=app_markers[app_name],
            markersize=8,
            lw=1.5,
            zorder=1,
        )

        # Plot a box for each platform supported by this application
        supported_platforms = list(app_df["platform"])
        xvalues = np.arange(1, len(supported_platforms) + 1)
        boxes = ax.bar(
            xvalues,
            height=fac,
            width=1,
            bottom=i * fac,
            edgecolor="black",
            color=[plat_colors[p] for p in supported_platforms],
            linewidth=1,
            zorder=2,
        )

        # Label the box with its associated platform
        for j, box in enumerate(boxes):
            ax.text(
                box.get_x() + box.get_width() * 0.5,
                box.get_y() + box.get_height() * 0.5,
                plat_labels[supported_platforms[j]],
                ha="center",
                va="center",
                c="black",
                zorder=3,
            )


def _pp_bars(ax, df, pp_column, colors, markers):
    """
    Plot a bar for the performance portability of each application,
    using the axes provided.
    """
    applications = df["application"].unique()

    ax.set_xticks([])
    ax.set_ylabel("Performance Portability", rotation=-90, labelpad=14)
    ax.set_ylim([0, 1.1])
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    ax.grid(visible=True)

    pp = p3.metrics.pp(df)

    edgecolors = [colors[app] for app in pp["application"]]
    ax.bar(
        pp["application"],
        pp[pp_column],
        color="white",
        edgecolor=edgecolors,
        zorder=3,
    )

    for app_name in applications:
        app_pp = pp[(pp["application"] == app_name)]
        ax.plot(
            app_name,
            app_pp[pp_column],
            color=colors[app_name],
            marker=markers[app_name],
            markersize=8,
            lw=1.5,
            zorder=4,
        )


def _get_colors(applications, kwarg):
    """
    Assign a color to each application based on supplied kwarg.
    """
    if isinstance(kwarg, str):
        cmap = getattr(plt.cm, kwarg)
    elif isinstance(kwarg, list):
        cmap = matplotlib.colors.ListedColormap(kwarg)
    elif isinstance(kwarg, matplotlib.colors.Colormap):
        cmap = kwarg
    else:
        raise ValueError("Unsupported type provided for colormap.")

    cmap = cmap.resampled(len(applications))
    colors = cmap(np.linspace(0, 1, len(applications)))
    return {app: color for app, color in zip(applications, colors)}


def cascade(df, eff=None, size=(6, 5), **kwargs):
    """
    Plot a `cascade`_ summarizing the efficiency and performance
    portability of each application in a DataFrame, highlighting
    differences in platform support across the applications.

    The cascade is plotted using the current pyplot figure,
    if one exists.

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

    size: 2-tuple of floats, default: (6, 5)
        The size of the plot, in backend-specific units.

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
            "Handling multiple problems is currently not implemented."
        )

    backend = kwargs["backend"]
    if backend == "pgfplots":
        return _cascade_tex(df, eff, **kwargs)

    kwargs.setdefault("platform_legend", Legend())
    plat_legend = kwargs["platform_legend"]
    plat_legend.kwargs.setdefault("ncols", 4)
    plat_legend.kwargs.setdefault("loc", "upper center")
    plat_legend.kwargs.setdefault("bbox_to_anchor", (0.5, 0.0))

    kwargs.setdefault("application_legend", Legend())
    app_legend = kwargs["application_legend"]

    kwargs.setdefault("platform_style", PlatformStyle())
    plat_style = kwargs["platform_style"]
    if not plat_style.colors:
        plat_style.colors = getattr(plt.cm, "RdBu")

    kwargs.setdefault("application_style", ApplicationStyle())
    app_style = kwargs["application_style"]
    if not app_style.colors:
        app_style.colors = getattr(plt.cm, "tab10")
    if not app_style.markers:
        app_style.markers = getattr(
            matplotlib.markers.MarkerStyle, "filled_markers"
        )

    # Choose the efficiency column based on eff parameter and available columns
    efficiency_columns = []
    for column in ["app eff", "arch eff"]:
        if column in df:
            efficiency_columns.append(column)
    if len(efficiency_columns) == 0:
        msg = "DataFrame does not contain an 'app eff' or 'arch eff' column."
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
    _require_numeric(df, [eff_column])

    # Keep only the most efficient (application, platform) results.
    key = ["problem", "platform", "application"]
    groups = df[key + [eff_column]].groupby(key)
    df = groups.agg(max)
    df.reset_index(inplace=True)

    platforms = df["platform"].unique()
    applications = df["application"].unique()

    # Create a 2x2 grid of subplots sharing axes
    fig = plt.figure(figsize=size)
    ratios = [6, len(applications) * 0.5]
    axes = fig.subplots(
        2,
        2,
        sharex="col",
        gridspec_kw={
            "hspace": 0,
            "wspace": 0.025,
            "height_ratios": ratios,
            "width_ratios": ratios,
        },
    )

    # Choose colors for each application
    app_colors = _get_colors(applications, app_style.colors)

    # Choose markers for each application
    markers = app_style.markers
    if not isinstance(markers, (list, tuple)):
        raise ValueError("Unsupported type provided for app_markers")
    app_markers = {app: color for app, color in zip(applications, markers)}

    # Choose colors for each platform
    plat_colors = _get_colors(platforms, plat_style.colors)

    # Choose labels for each platform
    plat_labels = dict(zip(platforms, string.ascii_uppercase))

    # Plot the efficiency cascade in the top-left (0, 0)
    app_handles = _efficiency_cascade(
        axes[0][0], df, eff_column, app_colors, app_markers
    )

    # Plot the platform chart in the bottom-left (1, 0)
    _platform_chart(
        axes[1][0],
        df,
        eff_column,
        app_colors,
        app_markers,
        plat_colors,
        plat_labels,
    )

    # Plot the performance portability bars in the top-right (0, 1)
    pp_column = eff_column.replace("eff", "pp")
    _pp_bars(axes[0][1], df, pp_column, app_colors, app_markers)

    # Disable the plot in the bottom-right corner (1, 1)
    fig.delaxes(axes[1][1])

    # Attach the application legend to the left of the platform chart
    axes[1][0].legend(
        handles=app_handles,
        loc="upper left",
        bbox_to_anchor=(1, 1),
        ncol=1,
        **app_legend.kwargs,
    )

    # Attach the platform legend to the position requested by kwargs
    legend_helper = _PlatformLegendHandler(plat_colors, plat_labels)
    plat_handles = [
        mpatches.Patch(color=plat_colors[p], label=p) for p in platforms
    ]
    fig.legend(
        handles=plat_handles,
        handler_map={mpatches.Patch: legend_helper},
        handlelength=1.0,
        **plat_legend.kwargs,
    )

    return MPLCascadePlot(fig, axes)


def _cascade_tex(df, eff=None, **kwargs):
    """
    Generate TeX file that generates a `cascade`_ using PGFPlots
    summarizing the efficiency and performance portability of each
    application in a DataFrame, highlighting differences in platform
    support across the applications.

    The TeX file can be rendered as a PDF using `pdflatex`.

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
            "Handling multiple problems is currently not implemented."
        )

    # Define 19 default markers for LaTeX plots
    default_markers = [
        "*, mark options={style={solid}}",
        "*, mark options={style={solid}, scale=1.5}",
        "triangle*, mark options={style={solid}, scale=1.5, rotate=180}",
        "triangle*, mark options={style={solid}, scale=1.5}",
        "triangle*, mark options={style={solid}, scale=1.5, rotate=90}",
        "triangle*, mark options={style={solid}, scale=1.5, rotate=270}",
        "pentagon*, mark options={style={solid}, scale=1.5}",
        "square*, mark options={style={solid}, scale=1.5}",
        "diamond*, mark options={style={solid}, scale=1.5}",
        "o, mark options={style={solid}, scale=1.5}",
        "square, mark options={style={solid}, scale=1.5}",
        "triangle, mark options={style={solid}, scale=1.5}",
        "diamond, mark options={style={solid}, scale=1.5}",
        "pentagon, mark options={style={solid}, scale=1.5}",
        "oplus, mark options={style={solid}, scale=1.5}",
        "otimes, mark options={style={solid}, scale=1.5}",
        "star, mark options={style={solid}, scale=1.5}",
        "x, mark options={style={solid}, scale=1.5}",
        "+, mark options={style={solid}, scale=1.5}",
    ]

    kwargs.setdefault("platform_legend", Legend())
    plat_legend = kwargs["platform_legend"]
    plat_legend.kwargs.setdefault("nrows", 4)

    kwargs.setdefault("platform_style", PlatformStyle())
    plat_style = kwargs["platform_style"]
    if not plat_style.colors:
        plat_style.colors = getattr(plt.cm, "RdBu")

    kwargs.setdefault("application_style", ApplicationStyle())
    app_style = kwargs["application_style"]
    if not app_style.colors:
        app_style.colors = getattr(plt.cm, "tab10")
    if not app_style.markers:
        app_style.markers = default_markers

    # Choose the efficiency column based on eff parameter and available columns
    efficiency_columns = []
    for column in ["app eff", "arch eff"]:
        if column in df:
            efficiency_columns.append(column)
    if len(efficiency_columns) == 0:
        msg = "DataFrame does not contain an 'app eff' or 'arch eff' column."
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
    _require_numeric(df, [eff_column])

    # Keep only the most efficient (application, platform) results.
    key = ["problem", "platform", "application"]
    groups = df[key + [eff_column]].groupby(key)
    df = groups.agg(max)
    df.reset_index(inplace=True)

    platforms = df["platform"].unique()
    applications = df["application"].unique()

    # create a mapping between applicaiton names and TeX friendly names
    # (without spaces and punctuation)
    map_tab = str.maketrans("", "", " !\"#$%&'()*+, -./\\:;<=>?@[]^_`{|}~")
    app_to_tex_name = {
        app: tex
        for app, tex in zip(
            applications,
            [str(app_name).translate(map_tab) for app_name in applications],
        )
    }

    # Choose colors for each application and then convert the dictionary to
    # TeX friendly names and RGB colors
    app_colors = _get_colors(applications, app_style.colors)
    app_colors_rgb = {}
    for k in app_colors:
        app_colors_rgb[app_to_tex_name[k]] = str(
            matplotlib.colors.to_rgb(app_colors[k])
        ).strip("()")

    # Build a dictionary of platforms to labels
    plat_labels = dict(zip(platforms, string.ascii_uppercase))

    # Choose colors for each platform and then convert the dictionary to RGB
    # colors using the platform labels
    plat_colors = _get_colors(platforms, plat_style.colors)
    plat_colors_rgb = {}
    for k in plat_colors:
        plat_colors_rgb[plat_labels[k]] = str(
            matplotlib.colors.to_rgb(plat_colors[k])
        ).strip("()")

    # Choose markers for each application
    markers = app_style.markers
    if not isinstance(markers, (list, tuple)):
        raise ValueError("Unsupported type provided for app_markers")

    # build a dictionary of app line specifications for TeX
    app_line_specs = {}
    for app, mark in zip(applications, markers):
        app_line_specs[
            app
        ] = f"{app_to_tex_name[app]}, thick, solid, mark={mark}"

    # Choose labels for each platform
    plat_labels = dict(zip(platforms, string.ascii_uppercase))

    # Set the number of rows in the platform key (if set)
    # NOTE: This is different to matplotlib because PGF plots uses columns,
    #       and then transposes (so columns become rows)
    plat_legend_nrows = plat_legend.kwargs["nrows"]

    plotylabel = ""
    if eff_column == "app eff":
        plotylabel = "Application Efficiency"
    elif eff_column == "arch eff":
        plotylabel = "Architectural Efficiency"
    else:
        msg = "Unexpected efficiency column name: %s"
        raise ValueError(msg % (eff_column))

    # Build an dictionary with "application name, [ data ]" for the
    # efficiency plot
    plot_effs = {}
    for app_name in applications:
        app_df = df[(df["application"] == app_name) & (df[eff_column] > 0.0)]
        app_df = app_df.sort_values(by=[eff_column], ascending=False)
        yvalues = app_df[eff_column]
        supported_platforms = list(app_df["platform"])
        xvalues = np.arange(1, len(supported_platforms) + 1)
        plot_effs[app_name] = tuple(zip(xvalues, yvalues))

    # Build a dictionary with "application name, (application name, qp)"
    # for the pp bar plot
    pp = p3.metrics.pp(df)
    pp_column = eff_column.replace("eff", "pp")
    pp_bars = {
        app: f"({app}, {app_pp})"
        for app, app_pp in zip(pp["application"], pp[pp_column])
    }

    # Build a dictionary with "application name, [ A, B, C, etc ]", etc
    # for the platform plot
    plat_plot = {}
    for i, app_name in enumerate(applications):
        app_df = df[(df["application"] == app_name) & (df[eff_column] > 0.0)]
        app_df = app_df.sort_values(by=[eff_column], ascending=False)
        supported_platforms = list(app_df["platform"])
        supported_alpha = [plat_labels[s] for s in supported_platforms]
        plat_plot[app_name] = supported_alpha

    # Build a jinja environment that can parse the TeX template
    latex_jinja_env = jinja2.Environment(
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        line_statement_prefix="%-",
        line_comment_prefix="%#",
        trim_blocks=True,
        autoescape=True,
        loader=jinja2.FileSystemLoader(
            os.path.dirname(p3.__file__) + "/plot/"
        ),
    )

    # Load the template.tex file
    template = latex_jinja_env.get_template("template.tex")

    # Render the template using the parameters generated above to a file
    return PGFCascadePlot(
        template.stream(
            plottitle="",
            plotheight="200pt",
            plotwidth="200pt",
            applicationcount=len(applications),
            platformcount=len(platforms),
            plotylabel=plotylabel,
            plat_colors=plat_colors_rgb,
            app_colors=app_colors_rgb,
            app_line_specs=app_line_specs,
            plot_effs=plot_effs,
            applications=", ".join(pp["application"]),
            pp_bars=pp_bars,
            plat_plot=plat_plot,
            plat_labels=plat_labels,
            plat_legend_nrows=plat_legend_nrows,
        )
    )
