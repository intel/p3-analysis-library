# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import unittest

from p3analysis.data._validation import _validate_coverage_json


class TestValidation(unittest.TestCase):
    """
    Test p3analysis.data.validation functionality.
    """

    def test_coverage_json_valid(self):
        """p3analysis.data.validation.coverage_json_valid"""
        json_string = '[{"file": "path", "id": "sha", "lines": [1, 2, 3, 5]}]'
        result_object = _validate_coverage_json(json_string)
        expected_object = [{"file": "path", "id": "sha", "lines": [1, 2, 3, 5]}]
        self.assertTrue(result_object == expected_object)

    def test_coverage_json_invalid(self):
        """p3analysis.data.validation.coverage_json_invalid"""
        json_string = '[{"file": "path", "id": "sha", "lines": [["1"]]}]'
        with self.assertRaises(ValueError):
            _validate_coverage_json(json_string)

        with self.assertRaises(TypeError):
            json_object = [{"file": "path", "id": "sha", "lines": [["1"]]}]
            _validate_coverage_json(json_object)


if __name__ == "__main__":
    unittest.main()
