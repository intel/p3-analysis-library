# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT
import matplotlib
import pandas as pd
from p3.plot import navchart
import unittest


class TestNavchart(unittest.TestCase):
    """
    Test p3.plot.navchart functionality.
    """

    def test_required_columns(self):
        """p3.plot.navchart.required_columns"""

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
            columns=["problem", "platform", "application", "app pp"]
        )
        with self.assertRaises(ValueError):
            navchart(pp, cd, eff="invalid")

    def test_options(self):
        """p3.plot.navchart.options"""

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

        navchart(pp, cd, app_cmap=cmap)
        navchart(pp, cd, app_cmap="tab10")
        navchart(pp, cd, app_cmap=["blue", "green"])
        with self.assertRaises(ValueError):
            navchart(pp, cd, app_cmap=1)


if __name__ == "__main__":
    unittest.main()
