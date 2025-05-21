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
        expected_object = [{"file": "path", "id": "sha", "used_lines": [1, 2, 3, 5], "unused_lines": []}]

        json_string = '[{"file": "path", "id": "sha", "used_lines": [1, 2, 3, 5], "unused_lines": []}]'
        result_object = _validate_coverage_json(json_string)
        self.assertTrue(result_object == expected_object)

        json_object = expected_object
        result_object = _validate_coverage_json(json_object)
        self.assertTrue(result_object == expected_object)

    def test_coverage_json_invalid(self):
        """p3analysis.data.validation.coverage_json_invalid"""
        json_string = '[{"file": "path", "id": "sha", "used_lines": [["1"]], "unused_lines": []}]'
        with self.assertRaises(ValueError):
            _validate_coverage_json(json_string)

        with self.assertRaises(ValueError):
            json_object = [{"file": "path", "id": "sha", "used_lines": [["1"]], "unused_lines": []}]
            _validate_coverage_json(json_object)

        # Check that we only accept strings, lists and dicts.
        with self.assertRaises(TypeError):
            _validate_coverage_json(3)

        # Check that we rejects dicts based on schema rather than type.
        with self.assertRaises(ValueError):
            _validate_coverage_json({})

if __name__ == "__main__":
    unittest.main()
