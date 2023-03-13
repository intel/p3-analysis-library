# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import json
import pandas as pd
from p3.metrics import divergence
import unittest


class TestDivergence(unittest.TestCase):
    """
    Test p3.data.divergence functionality.
    """

    def test_required_columns(self):
        """p3.data.divergence.required_columns"""
        df = pd.DataFrame()
        cov = pd.DataFrame()

        with self.assertRaises(ValueError):
            divergence(df, cov)

    def test_side_effects(self):
        """p3.data.divergence.side_effects"""
        key = 0
        data = {
            "problem": ["test"] * 2,
            "platform": ["A", "B"],
            "application": ["latest"] * 2,
            "coverage_key": [key] * 2,
        }
        df = pd.DataFrame(data)
        json_string = json.dumps(
            [
                {
                    "file": "0",
                    "regions": [
                        [0, 1, 1],
                    ],
                }
            ]
        )
        cov = pd.DataFrame({"coverage_key": [key], "coverage": [json_string]})

        df_before = df.copy(deep=True)
        cov_before = cov.copy(deep=True)

        result = divergence(df, cov)

        df_after = df.copy(deep=True)
        cov_after = cov.copy(deep=True)

        pd.testing.assert_frame_equal(df_before, df_after)
        pd.testing.assert_frame_equal(cov_before, cov_after)

    def test_divergence(self):
        """p3.data.divergence"""
        data = {
            "problem": ["test"] * 2,
            "platform": ["A", "B"],
            "application": ["latest"] * 2,
            "coverage_key": ["source1", "source2"],
        }
        df = pd.DataFrame(data)

        source1_json_string = json.dumps(
            [
                {
                    "file": "0",
                    "regions": [
                        [0, 10, 10],
                    ],
                }
            ]
        )

        source2_json_string = json.dumps(
            [
                {
                    "file": "0",
                    "regions": [
                        [0, 10, 10],
                    ],
                },
                {
                    "file": "1",
                    "regions": [
                        [0, 10, 10],
                    ],
                },
            ]
        )

        cov = pd.DataFrame(
            {
                "coverage_key": ["source1", "source2"],
                "coverage": [source1_json_string, source2_json_string],
            }
        )

        result = divergence(df, cov)

        expected_data = {
            "problem": ["test"],
            "application": ["latest"],
            "divergence": [0.5],
        }
        expected_result = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(result, expected_result)

    def test_divergence_single(self):
        """p3.data.divergence.single"""
        key = 0
        data = {
            "problem": ["test"],
            "platform": ["test"],
            "application": ["test"],
            "coverage_key": [key],
        }
        df = pd.DataFrame(data)

        json_string = json.dumps(
            [
                {
                    "file": "0",
                    "regions": [
                        [0, 1, 1],
                    ],
                }
            ]
        )
        cov = pd.DataFrame({"coverage_key": [key], "coverage": [json_string]})

        result = divergence(df, cov)

        expected_data = {
            "problem": ["test"],
            "application": ["test"],
            "divergence": [0],
        }
        expected_df = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(result, expected_df)


if __name__ == "__main__":
    unittest.main()
