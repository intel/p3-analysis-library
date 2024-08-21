# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import unittest

import pandas as pd

from p3.data import projection
from p3.data._projection import _collapse


class TestProjection(unittest.TestCase):
    """
    Test p3.data.projection functionality.
    """

    def test_collapse(self):
        """p3.data.projection.collapse"""
        data = {"c1": ["x", "y", "z"], "c2": ["1", "2", "3"]}
        df = pd.DataFrame(data)

        _collapse(df, ["c1", "c2"], "c3")

        expected_data = {"c3": ["x-1", "y-2", "z-3"]}
        expected_df = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(df, expected_df)

    def test_collapse_null(self):
        """Check that _collapse skips null values"""
        data = {"c1": ["x", "y", "z"], "c2": ["1", None, "3"]}
        df = pd.DataFrame(data)

        _collapse(df, ["c1", "c2"], "c3")

        expected_data = {"c3": ["x-1", "y", "z-3"]}
        expected_df = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(df, expected_df)

    def test_required_columns(self):
        """p3.data.projection.required_columns"""
        df = pd.DataFrame()

        with self.assertRaises(ValueError):
            projection(df, problem=["c1"])

        with self.assertRaises(ValueError):
            projection(df, application=["c1"])

        with self.assertRaises(ValueError):
            projection(df, platform=["c1"])

        with self.assertRaises(TypeError):
            projection(df, platform="c1")

        with self.assertRaises(TypeError):
            projection(df, platform=[1])

    def test_side_effects(self):
        """p3.data.projection.side_effects"""
        data = {
            "c1": ["x", "y"],
            "c2": ["1", "2"],
            "application": ["A", "B"],
            "platform": ["X", "Y"],
        }
        df = pd.DataFrame(data)

        df_before = df.copy(deep=True)
        result = projection(df, problem=["c1", "c2"])
        df_after = df.copy(deep=True)

        pd.testing.assert_frame_equal(df_before, df_after)

        with self.assertRaises(AssertionError):
            pd.testing.assert_frame_equal(df, result)

    def test_projection(self):
        """p3.data.projection"""
        data = {
            "c1": ["x", "y"],
            "c2": ["1", "2"],
            "c3": ["A", "B"],
            "c4": ["X", "Y"],
        }
        df = pd.DataFrame(data)

        prob = ["c1", "c2"]
        appl = ["c3"]
        plat = ["c4"]
        result = projection(df, problem=prob, application=appl, platform=plat)

        expected_data = {
            "problem": ["x-1", "y-2"],
            "application": ["A", "B"],
            "platform": ["X", "Y"],
        }
        expected_df = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(result, expected_df, check_like=True)

    def test_empty_projection(self):
        """p3.data.empty_projection"""
        data = {"problem": ["x"], "platform": ["X"], "application": ["A"]}
        df = pd.DataFrame(data)

        result = projection(df)

        expected_df = pd.DataFrame(data)
        pd.testing.assert_frame_equal(result, expected_df)


if __name__ == "__main__":
    unittest.main()
