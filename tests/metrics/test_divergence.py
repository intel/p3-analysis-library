# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import json
import unittest

import pandas as pd

from p3analysis.metrics import divergence


class TestDivergence(unittest.TestCase):
    """
    Test p3analysis.data.divergence functionality.
    """

    def test_required_columns(self):
        """Check that divergence() validates required columns."""
        df = pd.DataFrame()
        cov = pd.DataFrame()

        with self.assertRaises(ValueError):
            divergence(df, cov)

    def test_side_effects(self):
        """Check that divergence() has no side effects."""
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
                    "file": "file.cpp",
                    "id": "0",
                    "lines": [0],
                },
            ],
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
        """Check that divergence() produces expected results for valid data."""
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
                    "file": "foo.cpp",
                    "id": "0",
                    "lines": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                },
            ],
        )

        source2_json_string = json.dumps(
            [
                {
                    "file": "foo.cpp",
                    "id": "0",
                    "lines": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                },
                {
                    "file": "bar.cpp",
                    "id": "1",
                    "lines": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                },
            ],
        )

        cov = pd.DataFrame(
            {
                "coverage_key": ["source1", "source2"],
                "coverage": [source1_json_string, source2_json_string],
            },
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
        """Check that divergence() does not fail with only one platform."""
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
                    "file": "file.cpp",
                    "id": "0",
                    "lines": [0],
                },
            ],
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

    def test_divergence_duplicate(self):
        """Check that divergence() uses both file and id for uniqueness."""
        data = {
            "problem": ["test"] * 2,
            "platform": ["A", "B"],
            "application": ["latest"] * 2,
            "coverage_key": ["source1", "source2"],
        }
        df = pd.DataFrame(data)

        # First file called "foo.cpp" has an id of "0".
        source1_json_string = json.dumps(
            [
                {
                    "file": "foo.cpp",
                    "id": "0",
                    "lines": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                },
            ],
        )

        # Second file called "foo.cpp" has a different id ("1").
        # It should therefore be recognized as a different file.
        source2_json_string = json.dumps(
            [
                {
                    "file": "foo.cpp",
                    "id": "1",
                    "lines": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                },
            ],
        )

        cov = pd.DataFrame(
            {
                "coverage_key": ["source1", "source2"],
                "coverage": [source1_json_string, source2_json_string],
            },
        )

        result = divergence(df, cov)

        expected_data = {
            "problem": ["test"],
            "application": ["latest"],
            "divergence": [1.0],
        }
        expected_result = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(result, expected_result)


if __name__ == "__main__":
    unittest.main()
