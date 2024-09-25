# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT
"""
Contains objects for interacting with plots produced using the
:py:mod:`matplotlib` backend.
"""

import string

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.path import Path

import p3analysis.metrics
from p3analysis._utils import _cast_to_numeric
from p3analysis.plot._common import ApplicationStyle, Legend, PlatformStyle
from p3analysis.plot.backend import CascadePlot, NavChart


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


class CascadePlot(CascadePlot):
    """
    Cascade plot object for :py:mod:`matplotlib`.
    """

    def __init__(
        self,
        df,
        eff_column,
        size=None,
        fig=None,
        axes=None,
        **kwargs,
    ):
        super().__init__("matplotlib")

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
                matplotlib.markers.MarkerStyle,
                "filled_markers",
            )

        # If the size is unset, default to 6 x 5
        if not size:
            size = (6, 5)

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
        if len(applications) > len(markers):
            raise RuntimeError(
                f"The number of applications ({len(applications)}) is greater "
                f"than the number of markers ({len(markers)}). "
                + "Please adjust the ApplicationStyle.",
            )
        app_markers = {app: color for app, color in zip(applications, markers)}

        # Choose colors for each platform
        plat_colors = _get_colors(platforms, plat_style.colors)

        # Choose labels for each platform
        if len(platforms) > len(string.ascii_uppercase):
            raise RuntimeError(
                "The number of platforms supported by cascade plots is "
                + f"currently limited to {len(string.ascii_uppercase)}.",
            )
        plat_labels = dict(zip(platforms, string.ascii_uppercase))

        # Plot the efficiency cascade in the top-left (0, 0)
        app_handles = self.__efficiency_cascade(
            axes[0][0],
            df,
            eff_column,
            app_colors,
            app_markers,
        )

        # Plot the platform chart in the bottom-left (1, 0)
        self.__platform_chart(
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
        self.__pp_bars(axes[0][1], df, pp_column, app_colors, app_markers)

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

        self.fig = fig
        self.axes = axes

    def get_figure(self):
        """
        Returns
        -------
        :py:class:`matplotlib.figure.Figure`
            The :py:class:`matplotlib.figure.Figure` used for the plot.
        """
        return self.fig

    def get_axes(self, subplot="eff"):
        """
        Parameters
        ----------
        subplot: {'eff', 'pp', 'plat'}
            The name of the requested subplot. The options correspond to the
            efficiency cascade, performance portability bar chart, and platform
            chart, respectively.

        Returns
        -------
        :py:class:`matplotlib.axes.Axes`
            The :py:class:`matplotlib.axes.Axes` used for the specified
            subplot.
        """
        if subplot == "eff":
            return self.axes[0][0]
        if subplot == "pp":
            return self.axes[0][1]
        if subplot == "plat":
            return self.axes[1][0]
        msg = "Unrecognized subplot name: '%s'"
        raise ValueError(msg % (subplot))

    def __efficiency_cascade(self, ax, df, eff_column, colors, markers):
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
            app_df = df[
                (df["application"] == app_name) & (df[eff_column] > 0.0)
            ]
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

    def __platform_chart(
        self,
        ax,
        df,
        eff_column,
        app_colors,
        app_markers,
        plat_colors,
        plat_labels,
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
            app_df = df[
                (df["application"] == app_name) & (df[eff_column] > 0.0)
            ]
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

    def __pp_bars(self, ax, df, pp_column, colors, markers):
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

        pp = p3analysis.metrics.pp(df)

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

    def save(self, filename):
        """
        Save the plot to the specified file.

        Parameters
        ----------
        filename: string
        """
        self.fig.savefig(filename, bbox_inches="tight")


class NavChart(NavChart):
    """
    Navigation chart object for :py:mod:`matplotlib`.
    """

    def __init__(
        self,
        pp,
        cd,
        eff=None,
        size=None,
        goal=None,
        fig=None,
        axes=None,
        **kwargs,
    ):
        super().__init__("matplotlib")

        kwargs.setdefault("legend", Legend())
        legend = kwargs["legend"]
        legend.kwargs.setdefault("loc", "upper center")
        legend.kwargs.setdefault("bbox_to_anchor", (0.5, 0.0))

        kwargs.setdefault("style", ApplicationStyle())
        style = kwargs["style"]
        if not style.colors:
            style.colors = getattr(plt.cm, "tab10")
        if not style.markers:
            style.markers = getattr(
                matplotlib.markers.MarkerStyle,
                "filled_markers",
            )

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
            pp_column = eff + " pp"
            if pp_column not in pp:
                msg = "DataFrame does not contain an '%s' column."
                raise ValueError(msg % (pp_column))
        pp = _cast_to_numeric(pp, [pp_column])

        # If the size is unset, default to 5 x 5
        if not size:
            size = (5, 5)

        ppcd = pd.merge(pp, cd, on=["problem", "application"], how="inner")

        applications = ppcd["application"].unique()
        app_colors = _get_colors(applications, style.colors)

        markers = style.markers
        if not isinstance(markers, (list, tuple)):
            raise ValueError("Unsupported type provided for app_markers")
        if len(applications) > len(markers):
            raise RuntimeError(
                f"The number of applications ({len(applications)}) is greater "
                f"than the number of markers ({len(markers)}). "
                + "Please adjust the ApplicationStyle.",
            )
        app_markers = {
            app: marker for app, marker in zip(applications, markers)
        }

        # Add a small amount of jitter to make overlapping points less likely
        jitter = np.random.default_rng().uniform(0, 0.01, 2 * len(ppcd))

        fig = plt.figure(figsize=size)
        axes = plt.gca()
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
            axes.add_patch(patch)
            axes.plot(
                convergence + jitter_x,
                app_pp + jitter_y,
                color=app_colors[app_name],
                label=app_name,
                clip_on=False,
                marker=app_markers[app_name],
                markersize=8,
                zorder=10,
            )
        axes.grid(True)

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
            patch = mpatches.PathPatch(
                path,
                facecolor="yellow",
                lw=2,
                alpha=0.5,
            )
            axes.add_patch(patch)

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
            axes.set_ylabel("Performance Portability (App. Eff.)")
        elif pp_column == "arch pp":
            axes.set_ylabel("Performance Portability (Arch. Eff.)")
        axes.set_xlabel("Code Convergence")
        axes.set_ylim([0, 1])
        axes.set_xlim([0, 1])

        fig.legend(**legend.kwargs)

        self.fig = fig
        self.axes = axes

    def get_figure(self):
        """
        Returns
        -------
        :py:class:`matplotlib.figure.Figure`
            The :py:class:`matplotlib.figure.Figure` used for the chart.
        """
        return self.fig

    def get_axes(self):
        """
        Returns
        -------
        :py:class:`matplotlib.axes.Axes`
            The :py:class:`matplotlib.axes.Axes` used for the chart.
        """
        return self.axes

    def save(self, filename):
        """
        Save the plot to the specified file.

        Parameters
        ----------
        filename: string
        """
        self.fig.savefig(filename, bbox_inches="tight")
