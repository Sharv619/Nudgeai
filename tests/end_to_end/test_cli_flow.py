"""End-to-end: invoke the CLI as a subprocess."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "cli", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )


class CliEndToEndTests(unittest.TestCase):
    def test_help_lists_all_commands(self):
        r = run_cli("--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        for cmd in ("sync", "index", "query", "nudge", "summary", "status"):
            self.assertIn(cmd, r.stdout)

    def test_sync_help(self):
        r = run_cli("sync", "--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--source", r.stdout)
        self.assertIn("--save", r.stdout)

    def test_query_missing_arg_exits_nonzero(self):
        r = run_cli("query")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("query", r.stderr.lower())

    def test_sync_location_mock_returns_json(self):
        # Location sync falls back to mock data when no Google Takeout path is
        # available, so this runs offline.
        r = run_cli("--json", "sync", "--source", "location", "--days", "3")
        self.assertEqual(r.returncode, 0, r.stderr)
        payload = json.loads(r.stdout)
        self.assertIn("sync_summary", payload)
        self.assertIn("location", payload["sync_summary"])
        self.assertGreaterEqual(payload["sync_summary"]["location"], 0)


if __name__ == "__main__":
    unittest.main()
