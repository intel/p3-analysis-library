# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT
"""
Contains objects for interacting with plots produced using the
:py:mod:`matplotlib` backend.
"""

from . import CascadePlot
from . import NavChart


class CascadePlot(CascadePlot):
    """
    Cascade plot object for :py:mod:`matplotlib`.
    """

    def __init__(self, fig, axes):
        super().__init__("matplotlib")
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
        raise ValueError("Unrecognized subplot name: '%s'" % subplot)


class NavChart(NavChart):
    """
    Navigation chart object for :py:mod:`matplotlib`.
    """

    def __init__(self, fig, axes):
        super().__init__("matplotlib")
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
