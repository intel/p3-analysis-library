# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT
"""
Contains objects for interacting with plots produced using the
:py:mod:`pgfplots` backend.
"""

import string

import jinja2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import p3.metrics
from p3._utils import _require_numeric
from p3.plot._common import ApplicationStyle, Legend, PlatformStyle
from p3.plot.backend import CascadePlot, NavChart

# Define 19 default markers for LaTeX plots
_pgfplots_markers = [
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


def _get_tex_template(filename):
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
        loader=jinja2.PackageLoader("p3.plot.backend"),
    )

    # Load the template
    return latex_jinja_env.get_template(filename)


class CascadePlot(CascadePlot):
    """
    Cascade plot object for :py:mod:`pgfplots`.
    """

    def __init__(self, df, eff=None, size=None, stream=None, **kwargs):
        super().__init__("pgfplots")

        default_markers = _pgfplots_markers

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

        # Choose the efficiency column based on eff parameter and available
        # columns
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
        _require_numeric(df, [eff_column])

        # If the size is unset, default to 200pt x 200pt, otherwise set size
        plotwidth = "200pt"
        plotheight = "200pt"
        if size:
            plotwidth = size[0]
            plotheight = size[1]

        # Keep only the most efficient (application, platform) results.
        key = ["problem", "platform", "application"]
        groups = df[key + [eff_column]].groupby(key)
        df = groups.agg(max)
        df.reset_index(inplace=True)

        platforms = df["platform"].unique()
        applications = df["application"].unique()

        # Create a mapping between application names and TeX friendly names
        # (without spaces and punctuation)
        map_tab = str.maketrans("", "", " !\"#$%&'()*+, -./\\:;<=>?@[]^_`{|}~")
        app_to_tex_name = {
            app: tex
            for app, tex in zip(
                applications,
                [
                    str(app_name).translate(map_tab)
                    for app_name in applications
                ],
            )
        }

        # Choose colors for each application and then convert the dictionary to
        # TeX friendly names and RGB colors
        app_colors = _get_colors(applications, app_style.colors)
        app_colors_rgb = {}
        for k in app_colors:
            app_colors_rgb[app_to_tex_name[k]] = str(
                matplotlib.colors.to_rgb(app_colors[k]),
            ).strip("()")

        # Build a dictionary of platforms to labels
        plat_labels = dict(zip(platforms, string.ascii_uppercase))

        # Choose colors for each platform and then convert the dictionary to
        # RGB colors using the platform labels
        plat_colors = _get_colors(platforms, plat_style.colors)
        plat_colors_rgb = {}
        for k in plat_colors:
            plat_colors_rgb[plat_labels[k]] = str(
                matplotlib.colors.to_rgb(plat_colors[k]),
            ).strip("()")

        # Choose markers for each application
        markers = app_style.markers
        if not isinstance(markers, (list, tuple)):
            raise ValueError("Unsupported type provided for app_markers")

        # Build a dictionary of app line specifications for TeX
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

        # Build a dictionary with "application name, [ data ]" for the
        # efficiency plot
        plot_effs = {}
        for app_name in applications:
            app_df = df[
                (df["application"] == app_name) & (df[eff_column] > 0.0)
            ]
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

        # Build a dictionary with "application name, [ A, B, C, ... ]"
        # for the platform plot
        plat_plot = {}
        for i, app_name in enumerate(applications):
            app_df = df[
                (df["application"] == app_name) & (df[eff_column] > 0.0)
            ]
            app_df = app_df.sort_values(by=[eff_column], ascending=False)
            supported_platforms = list(app_df["platform"])
            supported_alpha = [plat_labels[s] for s in supported_platforms]
            plat_plot[app_name] = supported_alpha

        # Load the cascade.tex template
        template = _get_tex_template("cascade.tex")

        # Render the template using the parameters generated above
        self.stream = template.stream(
            plottitle="",
            plotwidth=plotwidth,
            plotheight=plotheight,
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

    def save(self, filename):
        """
        Save the plot to the specified file.

        Parameters
        ----------
        filename: string
        """
        self.stream.dump(filename)


class NavChart(NavChart):
    """
    Navigation chart object for :py:mod:`pgfplots`.
    """

    def __init__(
        self,
        pp,
        cd,
        eff=None,
        size=None,
        goal=None,
        stream=None,
        **kwargs,
    ):
        super().__init__("pgfplots")

        default_markers = _pgfplots_markers

        # Set up a default Legend, but no customisation is available yet
        kwargs.setdefault("legend", Legend())
        # legend = kwargs["legend"]

        kwargs.setdefault("style", ApplicationStyle())
        style = kwargs["style"]
        if not style.colors:
            style.colors = getattr(plt.cm, "tab10")
        if not style.markers:
            style.markers = default_markers

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

        # If the size is unset, default to 200pt x 200pt, otherwise set size
        plotwidth = "200pt"
        plotheight = "200pt"
        if size:
            plotwidth = size[0]
            plotheight = size[1]

        ppcd = pd.merge(pp, cd, on=["problem", "application"], how="inner")

        applications = ppcd["application"].unique()

        # Create a mapping between application names and TeX friendly names
        # (without spaces and punctuation)
        map_tab = str.maketrans("", "", " !\"#$%&'()*+, -./\\:;<=>?@[]^_`{|}~")
        app_to_tex_name = {
            app: tex
            for app, tex in zip(
                applications,
                [
                    str(app_name).translate(map_tab)
                    for app_name in applications
                ],
            )
        }

        # Choose colors for each application and then convert the dictionary to
        # TeX friendly names and RGB colors
        app_colors = _get_colors(applications, style.colors)
        app_colors_rgb = {}
        for k in app_colors:
            app_colors_rgb[app_to_tex_name[k]] = str(
                matplotlib.colors.to_rgb(app_colors[k]),
            ).strip("()")

        markers = style.markers
        if not isinstance(markers, (list, tuple)):
            raise ValueError("Unsupported type provided for app_markers")

        # Build a dictionary of app line specifications for TeX
        app_mark_specs = dict(zip(applications, markers))

        plotylabel = ""
        if pp_column == "app pp":
            plotylabel = "Performance Portability (App. Eff.)"
        elif pp_column == "arch pp":
            plotylabel = "Performance Portability (Arch. Eff.)"

        # Build a dictionary with "application name, coords"
        app_coords = {}
        for index, row in ppcd.iterrows():
            app_name = row["application"]
            app_pp = row[pp_column]
            convergence = 1 - row["divergence"]
            app_coords[app_name] = f"({convergence}, {app_pp})"

        # If a goal is set, set up the goal region variables
        goalset = False
        goalx = 1.0
        goaly = 1.0
        if goal and goal != (1, 1):
            goalset = True
            goalx = goal[0]
            goaly = goal[1]

        # Load the navchart.tex template
        template = _get_tex_template("navchart.tex")

        # Render the template using the parameters generated above
        self.stream = template.stream(
            plotwidth=plotwidth,
            plotheight=plotheight,
            plotylabel=plotylabel,
            goalset=goalset,
            goalx=goalx,
            goaly=goaly,
            applications=app_to_tex_name,
            app_colors=app_colors_rgb,
            app_mark_specs=app_mark_specs,
            app_coords=app_coords,
        )

    def save(self, filename):
        """
        Save the plot to the specified file.

        Parameters
        ----------
        filename: string
        """
        self.stream.dump(filename)
