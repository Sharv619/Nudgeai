import tempfile
import unittest
from pathlib import Path

import simple_api_server


class NudgeStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_path = simple_api_server.NUDGE_STORE_PATH
        simple_api_server.NUDGE_STORE_PATH = Path(self.temp_dir.name) / "nudges.json"

    def tearDown(self):
        simple_api_server.NUDGE_STORE_PATH = self.original_path
        self.temp_dir.cleanup()

    def test_save_and_load_nudges(self):
        nudge = {
            "id": "n1",
            "title": "Follow up",
            "status": "pending",
            "priority": "medium",
            "createdAt": "2026-06-17T00:00:00Z",
            "updatedAt": "2026-06-17T00:00:00Z",
            "last_notified_at": None,
            "notification_count": 0,
        }

        simple_api_server.save_nudges([nudge])

        self.assertEqual(simple_api_server.load_nudges(), [nudge])

    def test_empty_store_returns_empty_list(self):
        self.assertEqual(simple_api_server.load_nudges(), [])


if __name__ == "__main__":
    unittest.main()
