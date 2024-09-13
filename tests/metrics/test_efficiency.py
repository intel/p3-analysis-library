# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import unittest

import pandas as pd

from p3analysis.metrics import application_efficiency


class TestEfficiency(unittest.TestCase):
    """
    Test p3analysis.data.efficiency functionality.
    """

    def test_required_columns(self):
        """p3analysis.data.efficiency.required_columns"""
        df = pd.DataFrame()

        with self.assertRaises(ValueError):
            application_efficiency(df)

    def test_required_column_types(self):
        """Check that application_efficiency() validates column types."""
        data = {
            "problem": ["problem"],
            "platform": ["platform"],
            "application": ["application"],
            "fom": ["non-numeric"],
        }
        df = pd.DataFrame(data)

        with self.assertRaises(TypeError):
            application_efficiency(df)

    def test_foms(self):
        """p3analysis.data.efficiency.foms"""
        data = {"problem": [], "platform": [], "application": [], "fom": []}
        df = pd.DataFrame(data)

        with self.assertRaises(ValueError):
            application_efficiency(df, foms="invalid")

    def test_side_effects(self):
        """p3analysis.data.efficiency.side_effects"""
        data = {
            "problem": ["test"] * 10,
            "platform": ["A", "B", "C", "D", "E"] * 2,
            "application": ["latest"] * 5 + ["best"] * 5,
            "fom": [25.0, 12.5, 25.0, None, 5.0]
            + [25.0, 10.0, 12.5, 5.0, 1.0],
        }
        df = pd.DataFrame(data)

        df_before = df.copy(deep=True)
        result = application_efficiency(df, foms="lower")
        df_after = df.copy(deep=True)

        pd.testing.assert_frame_equal(df_before, df_after)

        with self.assertRaises(AssertionError):
            pd.testing.assert_frame_equal(df, result)

    def test_efficiency(self):
        """p3analysis.data.efficiency"""

        # Test foms = lower
        # fom interpretations are time
        data = {
            "problem": ["test"] * 10,
            "platform": ["A", "B", "C", "D", "E"] * 2,
            "application": ["latest"] * 5 + ["best"] * 5,
            "fom": [25.0, 12.5, 25.0, None, 5.0]
            + [25.0, 10.0, 12.5, 5.0, 1.0],
        }
        df = pd.DataFrame(data)

        result = application_efficiency(df, foms="lower")

        eff_data = {
            "app eff": [1.0, 0.8, 0.5, 0.0, 0.2] + [1.0, 1.0, 1.0, 1.0, 1.0],
        }
        expected_data = data.copy()
        expected_data.update(eff_data)
        expected_df = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(result, expected_df)

        # Test foms = higher
        # fom interpretations are GFLOP/s
        data = {
            "problem": ["test"] * 10,
            "platform": ["A", "B", "C", "D", "E"] * 2,
            "application": ["latest"] * 5 + ["best"] * 5,
            "fom": [4, 8, 4, 0, 20] + [4, 10, 8, 20, 100],
        }
        df = pd.DataFrame(data)

        result = application_efficiency(df, foms="higher")

        eff_data = {
            "app eff": [1.0, 0.8, 0.5, 0.0, 0.2] + [1.0, 1.0, 1.0, 1.0, 1.0],
        }
        expected_data = data.copy()
        expected_data.update(eff_data)
        expected_df = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(result, expected_df)

        # Test invalid data
        with self.assertRaises(ValueError):
            application_efficiency(df, foms="invalid")

        invalid_data = {
            "problem": ["test"] * 2,
            "platform": ["A", "B"],
            "application": ["latest"] * 2,
            "fom": ["invalid", 1],
        }
        df = pd.DataFrame(invalid_data)
        with self.assertRaises(TypeError):
            application_efficiency(df, foms="higher")


if __name__ == "__main__":
    unittest.main()
