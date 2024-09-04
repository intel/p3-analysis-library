# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT


class Legend:
    """
    Container for legend styling options.
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs


class ApplicationStyle:
    """
    Container for application styling options.
    """

    def __init__(self, colors=None, markers=None, **kwargs):
        self.colors = colors
        self.markers = markers
        self.kwargs = kwargs


class PlatformStyle:
    """
    Container for platform styling options.
    """

    def __init__(self, colors=None, **kwargs):
        self.colors = colors
        self.kwargs = kwargs
