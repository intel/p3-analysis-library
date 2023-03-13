# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT

import unittest

from p3.data._validation import _validate_coverage_json


class TestValidation(unittest.TestCase):
    """
    Test p3.data.validation functionality.
    """

    def test_coverage_json_valid(self):
        """p3.data.validation.coverage_json_valid"""
        json_string = '[{"file": "id", "regions": [[1,2,3]]}]'
        result_object = _validate_coverage_json(json_string)
        expected_object = [{"file": "id", "regions": [[1, 2, 3]]}]
        self.assertTrue(result_object == expected_object)

    def test_coverage_json_invalid(self):
        """p3.data.validation.coverage_json_invalid"""
        json_string = '[{"file": "id", "regions": [["1"]]}]'
        with self.assertRaises(ValueError):
            _validate_coverage_json(json_string)

        with self.assertRaises(TypeError):
            json_object = [{"file": "id", "regions": [[1, 2, 3]]}]
            _validate_coverage_json(json_object)


if __name__ == "__main__":
    unittest.main()
