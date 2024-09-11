# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT
import unittest

import matplotlib
import pandas as pd

from p3analysis.plot import ApplicationStyle, navchart


class TestNavchart(unittest.TestCase):
    """
    Test p3analysis.plot.navchart functionality.
    """

    def test_required_columns(self):
        """p3analysis.plot.navchart.required_columns"""

        pp = pd.DataFrame()
        cd = pd.DataFrame()
        with self.assertRaises(ValueError):
            navchart(pp, cd)

        pp = pd.DataFrame(columns=["problem", "platform", "application"])
        cd = pd.DataFrame(columns=["problem", "application", "divergence"])
        with self.assertRaises(ValueError):
            navchart(pp, cd, eff="app")
        with self.assertRaises(ValueError):
            navchart(pp, cd, eff="arch")

        pp = pd.DataFrame(
            columns=["problem", "platform", "application", "app pp"],
        )
        with self.assertRaises(ValueError):
            navchart(pp, cd, eff="invalid")

    def test_options(self):
        """p3analysis.plot.navchart.options"""

        perf = {
            "problem": ["test"] * 2,
            "platform": ["A", "B"],
            "application": ["X", "Y"],
            "app pp": [0, 1],
        }
        pp = pd.DataFrame(perf)

        div = {
            "problem": ["test"] * 2,
            "application": ["X", "Y"],
            "divergence": [1, 0],
        }
        cd = pd.DataFrame(div)

        cmap = matplotlib.colormaps["tab10"]
        astyle = ApplicationStyle()

        astyle.colors = cmap
        navchart(pp, cd, style=astyle)

        astyle.colors = "tab10"
        navchart(pp, cd, style=astyle)

        astyle.colors = ["blue", "green"]
        navchart(pp, cd, style=astyle)

        with self.assertRaises(ValueError):
            astyle.colors = 1
            navchart(pp, cd, style=astyle)


if __name__ == "__main__":
    unittest.main()
