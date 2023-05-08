# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT


class Plot:
    """
    Base class for plot objects, providing access to backend-specific objects
    that can be used for plot customization.
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
