import unittest
from p3.data._validation import _validate_coverage_data

class TestValidation(unittest.TestCase):
    """
    Test p3.data.validation functionality.
    """

    def test_coverage_json_valid(self):
        """p3.data.validation.coverage_json_valid"""
        json_string = '[{"file": "path", "id": "sha", "lines": [1, 2, [3, 5]]}]'
        result_object = _validate_coverage_data(json_string)
        expected_object = [{"file": "path", "id": "sha", "lines": [1, 2, [3, 5]]}]
        self.assertEqual(result_object, expected_object)

    def test_coverage_json_invalid(self):
        """p3.data.validation.coverage_json_invalid"""
        json_string = '[{"file": "path", "id": "sha", "lines": [["1"]]}]'
        with self.assertRaises(ValueError):
            _validate_coverage_data(json_string)

        invalid_json_string = '[{"file": "path", "id": "sha", "lines": [1, 2, [3, 5]]'
        with self.assertRaises(ValueError):
            _validate_coverage_data(invalid_json_string)

    def test_coverage_object_valid(self):
        """p3.data.validation.coverage_object_valid"""
        json_object = [{"file": "path", "id": "sha", "lines": [1, 2, [3, 5]]}]
        print(f"Testing valid object: {json_object}")
        result_object = _validate_coverage_data(json_object)
        expected_object = json_object
        self.assertEqual(result_object, expected_object)

    def test_coverage_object_invalid(self):
        """p3.data.validation.coverage_object_invalid"""
        json_object = [{"file": "path", "id": "sha", "lines": [["1"]]}]
        print(f"Testing invalid object: {json_object}")
        with self.assertRaises(ValueError):
            _validate_coverage_data(json_object)

        print("Testing invalid type")
        with self.assertRaises(TypeError):
            _validate_coverage_data(12345)  # Tipo non valido

if __name__ == "__main__":
    unittest.main()
