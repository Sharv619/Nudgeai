import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

import simple_api_server


class ContextRuleEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_paths = {
            "nudge": simple_api_server.NUDGE_STORE_PATH,
            "places": simple_api_server.PLACES_STORE_PATH,
            "rules": simple_api_server.CONTEXT_RULES_STORE_PATH,
            "rule_state": simple_api_server.RULE_STATE_STORE_PATH,
            "location": simple_api_server.CURRENT_LOCATION_STORE_PATH,
            "calendar": simple_api_server.CALENDAR_AVAILABILITY_STORE_PATH,
        }
        root = Path(self.temp_dir.name)
        simple_api_server.NUDGE_STORE_PATH = root / "nudges.json"
        simple_api_server.PLACES_STORE_PATH = root / "places.json"
        simple_api_server.CONTEXT_RULES_STORE_PATH = root / "context_rules.json"
        simple_api_server.RULE_STATE_STORE_PATH = root / "rule_state.json"
        simple_api_server.CURRENT_LOCATION_STORE_PATH = root / "current_location.json"
        simple_api_server.CALENDAR_AVAILABILITY_STORE_PATH = root / "calendar_availability.json"
        self.client = TestClient(simple_api_server.app)
        self.now = datetime(2026, 6, 17, 10, 0, tzinfo=timezone.utc)

    def tearDown(self):
        simple_api_server.NUDGE_STORE_PATH = self.original_paths["nudge"]
        simple_api_server.PLACES_STORE_PATH = self.original_paths["places"]
        simple_api_server.CONTEXT_RULES_STORE_PATH = self.original_paths["rules"]
        simple_api_server.RULE_STATE_STORE_PATH = self.original_paths["rule_state"]
        simple_api_server.CURRENT_LOCATION_STORE_PATH = self.original_paths["location"]
        simple_api_server.CALENDAR_AVAILABILITY_STORE_PATH = self.original_paths["calendar"]
        self.temp_dir.cleanup()

    def evaluate(self, location=None, calendar=None, rule_state=None, rule_updates=None):
        places = simple_api_server.demo_places()
        rules = simple_api_server.demo_context_rules()
        rule = rules[0]
        if rule_updates:
            rule.update(rule_updates)
        return simple_api_server.evaluate_context_rule(
            rule=rule,
            places=places,
            current_location=location or simple_api_server.demo_current_location(),
            calendar=calendar or simple_api_server.demo_calendar_availability(),
            rule_state=rule_state or [],
            now=self.now,
        )

    def test_haversine_distance_near_place(self):
        place = simple_api_server.demo_places()[0]
        location = simple_api_server.demo_current_location()
        distance = simple_api_server.distance_meters(location, place)
        self.assertLessEqual(distance, place["radiusMeters"])

    def test_haversine_distance_far_from_place(self):
        place = simple_api_server.demo_places()[0]
        far_location = {
            "latitude": -33.8568,
            "longitude": 151.2153,
            "source": "demo",
            "updatedAt": "2026-06-17T00:00:00Z",
        }
        distance = simple_api_server.distance_meters(far_location, place)
        self.assertGreater(distance, place["radiusMeters"])

    def test_rule_matches_when_near_free_inside_window_and_no_cooldown(self):
        result = self.evaluate()
        self.assertTrue(result["matched"])
        self.assertEqual(result["reasons"], [])

    def test_rule_does_not_match_when_far_from_place(self):
        result = self.evaluate(
            location={
                "latitude": -33.8568,
                "longitude": 151.2153,
                "source": "demo",
                "updatedAt": "2026-06-17T00:00:00Z",
            }
        )
        self.assertFalse(result["matched"])
        self.assertIn("outside", result["reasons"][0])

    def test_rule_does_not_match_when_calendar_busy(self):
        calendar = simple_api_server.demo_calendar_availability()
        calendar["freeForMinutes"] = 20
        result = self.evaluate(calendar=calendar)
        self.assertFalse(result["matched"])
        self.assertIn("Calendar is free", result["reasons"][0])

    def test_rule_does_not_match_outside_time_window(self):
        result = self.evaluate(rule_updates={"timeWindow": {"start": "12:00", "end": "13:00"}})
        self.assertFalse(result["matched"])
        self.assertIn("outside", result["reasons"][0])

    def test_rule_does_not_match_when_cooldown_active(self):
        result = self.evaluate(
            rule_state=[{"ruleId": "gym-opportunity", "lastFiredAt": "2026-06-17T09:00:00Z"}]
        )
        self.assertFalse(result["matched"])
        self.assertIn("cooldown", result["reasons"][0])

    def test_matching_rule_creates_one_nudge_and_cooldown_prevents_duplicate(self):
        rules = simple_api_server.demo_context_rules()
        rules[0]["timeWindow"] = {"start": "00:00", "end": "23:59"}
        simple_api_server.save_context_rules(rules)

        first = self.client.post("/api/context-rules/evaluate")
        self.assertEqual(first.status_code, 200)
        self.assertTrue(first.json()["created"])
        self.assertIsNotNone(first.json()["evaluations"][0]["createdNudgeId"])

        second = self.client.post("/api/context-rules/evaluate")
        self.assertEqual(second.status_code, 200)
        self.assertFalse(second.json()["created"])

        listed = self.client.get("/api/nudges")
        self.assertEqual(listed.json()["count"], 1)


if __name__ == "__main__":
    unittest.main()
