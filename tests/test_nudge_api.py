import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import simple_api_server


class NudgeApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_path = simple_api_server.NUDGE_STORE_PATH
        self.original_places_path = simple_api_server.PLACES_STORE_PATH
        self.original_rules_path = simple_api_server.CONTEXT_RULES_STORE_PATH
        self.original_rule_state_path = simple_api_server.RULE_STATE_STORE_PATH
        self.original_location_path = simple_api_server.CURRENT_LOCATION_STORE_PATH
        self.original_calendar_path = simple_api_server.CALENDAR_AVAILABILITY_STORE_PATH
        simple_api_server.NUDGE_STORE_PATH = Path(self.temp_dir.name) / "nudges.json"
        simple_api_server.PLACES_STORE_PATH = Path(self.temp_dir.name) / "places.json"
        simple_api_server.CONTEXT_RULES_STORE_PATH = Path(self.temp_dir.name) / "context_rules.json"
        simple_api_server.RULE_STATE_STORE_PATH = Path(self.temp_dir.name) / "rule_state.json"
        simple_api_server.CURRENT_LOCATION_STORE_PATH = Path(self.temp_dir.name) / "current_location.json"
        simple_api_server.CALENDAR_AVAILABILITY_STORE_PATH = Path(self.temp_dir.name) / "calendar_availability.json"
        self.client = TestClient(simple_api_server.app)

    def tearDown(self):
        simple_api_server.NUDGE_STORE_PATH = self.original_path
        simple_api_server.PLACES_STORE_PATH = self.original_places_path
        simple_api_server.CONTEXT_RULES_STORE_PATH = self.original_rules_path
        simple_api_server.RULE_STATE_STORE_PATH = self.original_rule_state_path
        simple_api_server.CURRENT_LOCATION_STORE_PATH = self.original_location_path
        simple_api_server.CALENDAR_AVAILABILITY_STORE_PATH = self.original_calendar_path
        self.temp_dir.cleanup()

    def test_create_list_update_and_delete_nudge(self):
        created = self.client.post(
            "/api/nudges",
            json={"title": "Follow up with Priya", "priority": "high"},
        )
        self.assertEqual(created.status_code, 201)
        nudge = created.json()["nudge"]
        self.assertEqual(nudge["status"], "pending")
        self.assertEqual(nudge["source"], "manual")

        listed = self.client.get("/api/nudges")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json()["count"], 1)

        patched = self.client.patch(
            f"/api/nudges/{nudge['id']}",
            json={"status": "completed"},
        )
        self.assertEqual(patched.status_code, 200)
        self.assertEqual(patched.json()["nudge"]["status"], "completed")
        self.assertIsNotNone(patched.json()["nudge"]["completedAt"])

        deleted = self.client.delete(f"/api/nudges/{nudge['id']}")
        self.assertEqual(deleted.status_code, 200)
        self.assertTrue(deleted.json()["deleted"])

    def test_missing_title_returns_validation_error(self):
        response = self.client.post("/api/nudges", json={"priority": "medium"})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "validation_error")

    def test_extract_returns_reviewable_suggestions_for_valid_text(self):
        text = "Met Priya at the AI meetup. Need to send portfolio tomorrow and follow up next week."
        with patch.dict(simple_api_server.os.environ, {"EXTRACT_LLM_PROVIDER": "rules"}):
            response = self.client.post("/api/extract", json={"text_content": text})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["source"], "rules")
        self.assertGreaterEqual(payload["count"], 1)
        suggestion = payload["suggestions"][0]
        self.assertIn("title", suggestion)
        self.assertIn("due_date", suggestion)
        self.assertIn("confidence_score", suggestion)
        self.assertIn("reasoning", suggestion)
        self.assertIn("ai_note", suggestion)
        self.assertGreaterEqual(suggestion["confidence_score"], 0.0)
        self.assertLessEqual(suggestion["confidence_score"], 1.0)

    def test_extract_rejects_blank_text(self):
        response = self.client.post("/api/extract", json={"text_content": "   "})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "validation_error")

    def test_extract_rejects_malformed_text(self):
        response = self.client.post("/api/extract", json={"text_content": {"not": "a string"}})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["code"], "validation_error")

    def test_notification_poll_alerts_once_for_due_nudge(self):
        due_at = simple_api_server.to_iso_z(datetime.now(timezone.utc))
        created = self.client.post(
            "/api/nudges",
            json={"title": "Submit application", "context": "Deadline is today", "dueAt": due_at},
        )
        self.assertEqual(created.status_code, 201)
        nudge_id = created.json()["nudge"]["id"]

        first_poll = self.client.get("/api/notifications/poll")
        self.assertEqual(first_poll.status_code, 200)
        alerts = first_poll.json()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["id"], nudge_id)
        self.assertEqual(alerts[0]["type"], "due_today")

        second_poll = self.client.get("/api/notifications/poll")
        self.assertEqual(second_poll.status_code, 200)
        self.assertEqual(second_poll.json(), [])

        listed = self.client.get("/api/nudges")
        stored = listed.json()["nudges"][0]
        self.assertIsNotNone(stored["last_notified_at"])
        self.assertEqual(stored["notification_count"], 1)

    def test_notification_poll_alerts_once_for_context_rule_nudge(self):
        nudge = simple_api_server.create_nudge_record(
            title="Gym opportunity",
            context="Gym Opportunity: You're near the gym and free.",
            source="context_rule",
        )
        simple_api_server.save_nudges([nudge])

        first_poll = self.client.get("/api/notifications/poll")
        self.assertEqual(first_poll.status_code, 200)
        alerts = first_poll.json()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["id"], nudge["id"])
        self.assertEqual(alerts[0]["type"], "context_rule")

        second_poll = self.client.get("/api/notifications/poll")
        self.assertEqual(second_poll.status_code, 200)
        self.assertEqual(second_poll.json(), [])

    def test_notification_state_resets_when_due_time_changes(self):
        due_at = simple_api_server.to_iso_z(datetime.now(timezone.utc))
        created = self.client.post(
            "/api/nudges",
            json={"title": "Pay invoice", "context": "Payment due", "dueAt": due_at},
        )
        nudge_id = created.json()["nudge"]["id"]

        self.assertEqual(len(self.client.get("/api/notifications/poll").json()), 1)
        self.assertEqual(self.client.get("/api/notifications/poll").json(), [])

        patched = self.client.patch(f"/api/nudges/{nudge_id}", json={"dueAt": due_at})
        self.assertEqual(patched.status_code, 200)
        self.assertIsNone(patched.json()["nudge"]["last_notified_at"])
        self.assertEqual(patched.json()["nudge"]["notification_count"], 0)

        self.assertEqual(len(self.client.get("/api/notifications/poll").json()), 1)

    def test_context_status_and_manual_inputs(self):
        response = self.client.get("/api/source-status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sourceStatus"]["location"]["status"], "demo")
        self.assertEqual(response.json()["sourceStatus"]["calendar"]["status"], "demo")

        location = self.client.post(
            "/api/current-location",
            json={"latitude": -33.8688, "longitude": 151.2093, "source": "manual", "label": "Gym test"},
        )
        self.assertEqual(location.status_code, 200)
        self.assertEqual(location.json()["currentLocation"]["label"], "Gym test")

        calendar = self.client.patch(
            "/api/context/calendar",
            json={"mode": "manual", "freeForMinutes": 90},
        )
        self.assertEqual(calendar.status_code, 200)
        self.assertEqual(calendar.json()["calendar"]["freeForMinutes"], 90)

    def test_update_place_and_context_rule(self):
        place = self.client.patch(
            "/api/places/gym-demo",
            json={"name": "Edited Gym", "radiusMeters": 450, "enabled": False},
        )
        self.assertEqual(place.status_code, 200)
        self.assertEqual(place.json()["place"]["name"], "Edited Gym")
        self.assertEqual(place.json()["place"]["radiusMeters"], 450)
        self.assertFalse(place.json()["place"]["enabled"])

        rule = self.client.patch(
            "/api/context-rules/gym-opportunity",
            json={
                "requiredFreeMinutes": 60,
                "cooldownMinutes": 120,
                "timeWindow": {"start": "07:00", "end": "21:00"},
                "nudgeTemplate": {
                    "title": "Edited gym opportunity",
                    "context": "You're nearby and have time.",
                    "priority": "high",
                },
            },
        )
        self.assertEqual(rule.status_code, 200)
        self.assertEqual(rule.json()["rule"]["requiredFreeMinutes"], 60)
        self.assertEqual(rule.json()["rule"]["cooldownMinutes"], 120)
        self.assertEqual(rule.json()["rule"]["timeWindow"]["start"], "07:00")
        self.assertEqual(rule.json()["rule"]["nudgeTemplate"]["priority"], "high")

    def test_gym_opportunity_creates_nudge_and_respects_cooldown(self):
        rules = simple_api_server.load_context_rules()
        rules[0]["timeWindow"] = {"start": "00:00", "end": "23:59"}
        simple_api_server.save_context_rules(rules)

        created = self.client.post("/api/context-rules/evaluate")
        self.assertEqual(created.status_code, 200)
        payload = created.json()
        self.assertTrue(payload["created"])
        self.assertEqual(payload["nudge"]["source"], "context_rule")

        listed = self.client.get("/api/nudges")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json()["count"], 1)

        cooled_down = self.client.post("/api/context-rules/evaluate")
        self.assertEqual(cooled_down.status_code, 200)
        self.assertFalse(cooled_down.json()["created"])
        self.assertIn("cooldown", cooled_down.json()["evaluations"][0]["reasons"][0])

    def test_nudge_summary_returns_counts_minimal_items_and_source_status(self):
        due_at = simple_api_server.to_iso_z(datetime.now(timezone.utc) + timedelta(hours=1))
        overdue_at = simple_api_server.to_iso_z(datetime(2020, 1, 1, tzinfo=timezone.utc))
        self.client.post(
            "/api/nudges",
            json={"title": "High priority today", "priority": "high", "dueAt": due_at},
        )
        self.client.post(
            "/api/nudges",
            json={"title": "Old overdue item", "priority": "medium", "dueAt": overdue_at},
        )
        self.client.post(
            "/api/nudges",
            json={"title": "Low backlog", "priority": "low"},
        )

        response = self.client.get("/api/nudges/summary")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["counts"]["total"], 3)
        self.assertEqual(payload["counts"]["pending"], 3)
        self.assertEqual(payload["counts"]["due_today"], 1)
        self.assertEqual(payload["counts"]["overdue"], 1)
        self.assertIn("generatedAt", payload)
        self.assertEqual(payload["sourceStatus"]["location"]["status"], "demo")
        self.assertEqual(payload["sourceStatus"]["calendar"]["status"], "demo")
        self.assertGreaterEqual(len(payload["topItems"]), 1)
        first_item = payload["topItems"][0]
        self.assertEqual(first_item["title"], "High priority today")
        self.assertEqual(first_item["priority"], "high")
        self.assertIn("id", first_item)
        self.assertNotIn("context", first_item)
        self.assertNotIn("last_notified_at", first_item)


if __name__ == "__main__":
    unittest.main()
