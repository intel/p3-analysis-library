# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT
"""
Contains objects for interacting with plots produced using the
:py:mod:`pgfplots` backend.
"""

from . import CascadePGFPlot


class CascadePGFPlot(CascadePGFPlot):
    """
    Cascade plot object for :py:mod:`pgfplots`.
    """

    def __init__(self, stream):
        super().__init__("pgfplots")
        self.stream = stream

    def save(self, filename):
        """
        Save the plot to the specified file.

        Parameters
        ----------
        filename: string
        """
        self.stream.dump(filename)
