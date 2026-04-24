"""Unit tests for simple_api_server helper functions."""

import json
import os
import tempfile
import unittest

from simple_api_server import parse_duration_hours, safe_load_json_file


class ParseDurationHoursTests(unittest.TestCase):
    def test_hours_only(self):
        self.assertEqual(parse_duration_hours("16h"), 16.0)

    def test_minutes_only(self):
        self.assertAlmostEqual(parse_duration_hours("30m"), 0.5)

    def test_hours_and_minutes(self):
        self.assertAlmostEqual(parse_duration_hours("1h30m"), 1.5)

    def test_unknown_returns_zero(self):
        self.assertEqual(parse_duration_hours("Unknown"), 0.0)
        self.assertEqual(parse_duration_hours("N/A"), 0.0)
        self.assertEqual(parse_duration_hours(""), 0.0)
        self.assertEqual(parse_duration_hours(None), 0.0)

    def test_bare_number(self):
        self.assertEqual(parse_duration_hours("2"), 2.0)

    def test_garbage_returns_zero(self):
        self.assertEqual(parse_duration_hours("abc"), 0.0)


class SafeLoadJsonFileTests(unittest.TestCase):
    def test_missing_file_returns_empty_list(self):
        self.assertEqual(safe_load_json_file("/no/such/file.json"), [])

    def test_invalid_json_returns_empty_list(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write("{not json")
            path = f.name
        try:
            self.assertEqual(safe_load_json_file(path), [])
        finally:
            os.unlink(path)

    def test_valid_json_returns_payload(self):
        payload = [{"id": 1}, {"id": 2}]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(payload, f)
            path = f.name
        try:
            self.assertEqual(safe_load_json_file(path), payload)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
