# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT
import matplotlib
import pandas as pd
from p3.plot import cascade
import unittest


class TestCascade(unittest.TestCase):
    """
    Test p3.plot.cascade functionality.
    """

    def test_required_columns(self):
        """p3.plot.cascade.required_columns"""

        df = pd.DataFrame()
        with self.assertRaises(ValueError):
            cascade(df)

        required_columns = ["problem", "platform", "application"]
        df = pd.DataFrame(columns=required_columns)
        with self.assertRaises(ValueError):
            cascade(df, eff="app")
        with self.assertRaises(ValueError):
            cascade(df, eff="arch")

        df = pd.DataFrame(columns=required_columns + ["app eff"])
        with self.assertRaises(ValueError):
            cascade(df, eff="invalid")

    def test_options(self):
        """p3.plot.cascade.options"""

        data = {
            "problem": ["test"] * 2,
            "platform": ["A", "B"],
            "application": ["X", "Y"],
            "app eff": [0, 1],
        }
        df = pd.DataFrame(data)
        cmap = matplotlib.colormaps["tab10"]

        cascade(df, app_cmap=cmap)
        cascade(df, app_cmap="tab10")
        cascade(df, app_cmap=["blue", "green"])
        with self.assertRaises(ValueError):
            cascade(df, app_cmap=1)

        cascade(df, plat_cmap=cmap)
        cascade(df, plat_cmap="tab10")
        cascade(df, plat_cmap=["blue", "green"])
        with self.assertRaises(ValueError):
            cascade(df, plat_cmap=1)

        cascade(df, app_markers=[">", "<"])
        with self.assertRaises(ValueError):
            cascade(df, app_markers=1)

if __name__ == "__main__":
    unittest.main()
