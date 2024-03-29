# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT
"""
Contains backend-specific interfaces for customizing plots.

.. TIP::
   If you have any trouble customizing a plot, or the objects in this module
   do not provide access to the internals you are looking for, then please
   `open an issue
   <https://github.com/intel/p3-analysis-library/issues/new/choose>`_.
"""

__all__ = [
    "Plot",
    "CascadePlot",
    "NavChart",
]


class Plot:
    """
    Base class for plot objects.
    """

    def __init__(self, backend):
        self.backend = backend

    def get_backend(self):
        """
        Returns
        -------
        str
            The name of the backend used to generate the plot.
        """
        return self.backend


class CascadePlot(Plot):
    """
    Base class for cascade plot objects.
    """

    def __init__(self, backend):
        super().__init__(backend)


class NavChart(Plot):
    """
    Base class for navigation chart objects.
    """

    def __init__(self, backend):
        super().__init__(backend)
