# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import pandas as pd
from p3.metrics import pp
import unittest


class TestPP(unittest.TestCase):
    """
    Test p3.data.pp functionality.
    """

    def test_required_columns(self):
        """p3.data.pp.required_columns"""
        df = pd.DataFrame()

        with self.assertRaises(ValueError):
            pp(df)

    def test_effs(self):
        """p3.data.pp.effs"""
        data = {
            "problem": ["test"],
            "platform": ["test"],
            "application": ["test"],
            "app eff": [50],
            "arch eff": [0.5],
        }
        df = pd.DataFrame(data)

        with self.assertRaises(ValueError):
            pp(df)

        data = {
            "problem": ["test"],
            "platform": ["test"],
            "application": ["test"],
            "app eff": [0.5],
            "arch eff": [50],
        }
        df = pd.DataFrame(data)

        with self.assertRaises(ValueError):
            pp(df)

    def test_side_effects(self):
        """p3.data.pp.side_effects"""
        data = {
            "problem": ["test"] * 15,
            "platform": ["A", "B", "C", "D", "E"] * 3,
            "application": ["latest"] * 5 + ["best"] * 5 + ["dummy"] * 5,
            "fom": [25.0, 12.5, 25.0, 5.0, 5.0]
            + [25.0, 10.0, 12.5, 5.0, 1.0]
            + [25.0, 12.5, 25.0, None, 5.0],
            "app eff": [1.0, 0.8, 0.5, 1.0, 0.2]
            + [1.0, 1.0, 1.0, 1.0, 1.0]
            + [1.0, 0.8, 0.5, 0.0, 0.2],
            "arch eff": [0.0] * 15,
        }
        df = pd.DataFrame(data)

        df_before = df.copy(deep=True)
        result = pp(df)
        df_after = df.copy(deep=True)

        pd.testing.assert_frame_equal(df_before, df_after)

        with self.assertRaises(AssertionError):
            pd.testing.assert_frame_equal(df, result)

    def test_pp(self):
        """p3.data.pp"""

        data = {
            "problem": ["test"] * 15,
            "platform": ["A", "B", "C", "D", "E"] * 3,
            "application": ["latest"] * 5 + ["best"] * 5 + ["dummy"] * 5,
            "fom": [25.0, 12.5, 25.0, 5.0, 5.0]
            + [25.0, 10.0, 12.5, 5.0, 1.0]
            + [25.0, 12.5, 25.0, None, 5.0],
            "app eff": [1.0, 0.8, 0.5, 1.0, 0.2]
            + [1.0, 1.0, 1.0, 1.0, 1.0]
            + [1.0, 0.8, 0.5, 0.0, 0.2],
            "arch eff": [0.0] * 15,
        }
        df = pd.DataFrame(data)

        result = pp(df)

        expected_data = {
            "problem": ["test"] * 3,
            "application": ["best", "dummy", "latest"],
            "app pp": [1.0, 0.0, 0.4878],
            "arch pp": [0.0] * 3,
        }
        expected_df = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(result, expected_df)

        invalid_data = {
            "problem": ["test"] * 2,
            "platform": ["A", "B"],
            "application": ["latest"] * 2,
            "app eff": ["invalid", 1.0],
        }
        df = pd.DataFrame(invalid_data)
        with self.assertRaises(TypeError):
            pp(df)

    def test_pp_single(self):
        """p3.data.pp.single"""

        # Regression for trivial case with one record
        data = {
            "problem": ["test"],
            "platform": ["A"],
            "application": ["latest"],
            "fom": [25.0],
            "app eff": [0.2],
            "arch eff": [0.5],
        }
        df = pd.DataFrame(data)

        result = pp(df)

        expected_data = {
            "problem": ["test"],
            "application": ["latest"],
            "app pp": [0.2],
            "arch pp": [0.5],
        }
        expected_df = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(result, expected_df)


if __name__ == "__main__":
    unittest.main()
