# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT
import unittest

import matplotlib
import pandas as pd

from p3analysis.plot import ApplicationStyle, PlatformStyle, cascade


class TestCascade(unittest.TestCase):
    """
    Test p3analysis.plot.cascade functionality.
    """

    def test_required_columns(self):
        """p3analysis.plot.cascade.required_columns"""

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

    def test_required_column_types(self):
        """Check that cascade() validates column types."""
        data = {
            "problem": ["problem"],
            "platform": ["platform"],
            "application": ["application"],
            "app eff": ["non-numeric"],
        }
        df = pd.DataFrame(data)

        with self.assertRaises(TypeError):
            cascade(df, eff="app")

    def test_options(self):
        """p3analysis.plot.cascade.options"""

        data = {
            "problem": ["test"] * 2,
            "platform": ["A", "B"],
            "application": ["X", "Y"],
            "app eff": [0, 1],
        }
        df = pd.DataFrame(data)
        cmap = matplotlib.colormaps["tab10"]

        astyle = ApplicationStyle()
        pstyle = PlatformStyle()

        astyle.colors = cmap
        cascade(df, application_style=astyle)

        astyle.colors = "tab10"
        cascade(df, application_style=astyle)

        astyle.colors = ["blue", "green"]
        cascade(df, application_style=astyle)
        with self.assertRaises(ValueError):
            astyle.colors = 1
            cascade(df, application_style=astyle)

        pstyle.colors = cmap
        cascade(df, platform_style=pstyle)

        pstyle.colors = "tab10"
        cascade(df, platform_style=pstyle)

        pstyle.colors = ["blue", "green"]
        cascade(df, platform_style=pstyle)

        with self.assertRaises(ValueError):
            pstyle.colors = 1
            cascade(df, platform_style=pstyle)

        astyle = ApplicationStyle()
        astyle.markers = [">", "<"]
        cascade(df, application_style=astyle)

        with self.assertRaises(ValueError):
            astyle.markers = 1
            cascade(df, application_style=astyle)

if __name__ == "__main__":
    unittest.main()
