"""Unit tests for cli.main argparse + helpers."""

import unittest

from cli.main import _parse_filters, build_parser


class ParseFiltersTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(_parse_filters([]), {})

    def test_single_pair(self):
        self.assertEqual(_parse_filters(["type=calendar_event"]), {"type": "calendar_event"})

    def test_multi_pairs_strip_whitespace(self):
        out = _parse_filters([" type = fitness_activity ", "source=fit"])
        self.assertEqual(out, {"type": "fitness_activity", "source": "fit"})

    def test_value_may_contain_equals(self):
        self.assertEqual(_parse_filters(["url=https://x?a=1"]), {"url": "https://x?a=1"})

    def test_invalid_no_equals_raises(self):
        with self.assertRaises(SystemExit):
            _parse_filters(["nope"])


class CliParserTests(unittest.TestCase):
    def setUp(self):
        self.p = build_parser()

    def test_query_required(self):
        args = self.p.parse_args(["query", "find meeting"])
        self.assertEqual(args.command, "query")
        self.assertEqual(args.query, "find meeting")
        self.assertEqual(args.k, 5)

    def test_query_with_filters_and_k(self):
        args = self.p.parse_args(
            ["query", "gym", "-k", "2", "--filter", "type=fitness_activity"]
        )
        self.assertEqual(args.k, 2)
        self.assertEqual(args.filter, ["type=fitness_activity"])

    def test_sync_source_choice_enforced(self):
        with self.assertRaises(SystemExit):
            self.p.parse_args(["sync", "--source", "bogus"])

    def test_sync_defaults(self):
        args = self.p.parse_args(["sync"])
        self.assertIsNone(args.source)
        self.assertEqual(args.days, 14)
        self.assertEqual(args.max_results, 15)
        self.assertFalse(args.save)

    def test_global_json_flag(self):
        args = self.p.parse_args(["--json", "status"])
        self.assertTrue(args.json)

    def test_summary_optional_date(self):
        args = self.p.parse_args(["summary", "--date", "2026-04-25"])
        self.assertEqual(args.date, "2026-04-25")

    def test_index_types(self):
        args = self.p.parse_args(["index", "--types", "calendar", "fit"])
        self.assertEqual(args.types, ["calendar", "fit"])


if __name__ == "__main__":
    unittest.main()
