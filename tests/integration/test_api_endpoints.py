"""Integration tests: simple_api_server endpoints via FastAPI TestClient."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from simple_api_server import app


class ApiEndpointsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_aliases(self):
        for path in ("/health", "/api/health"):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
            self.assertEqual(r.json(), {"status": "healthy"})

    def test_calendar_alias_shape(self):
        for path in ("/api/mcp/tools/query_calendar", "/api/calendar"):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
            body = r.json()
            self.assertIn("result", body)
            self.assertIn("events", body["result"])
            self.assertIsInstance(body["result"]["events"], list)

    def test_location_alias_shape(self):
        for path in ("/api/mcp/tools/query_location", "/api/location"):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
            self.assertIn("locations", r.json()["result"])

    def test_drive_alias_shape(self):
        for path in ("/api/mcp/tools/query_drive", "/api/drive"):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
            self.assertIn("documents", r.json()["result"])

    def test_fit_alias_shape(self):
        for path in ("/api/mcp/tools/query_fit", "/api/fit"):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, path)
            health = r.json()["result"]["health"]
            self.assertIn("steps_today", health)
            self.assertIn("weekly_steps", health)
            self.assertEqual(len(health["weekly_steps"]), 7)

    def test_insights_default_focus(self):
        r = self.client.get("/api/insights")
        self.assertEqual(r.status_code, 200)
        ins = r.json()["result"]["insights"]
        self.assertIn("patterns", ins)
        self.assertIn("recommendations", ins)
        self.assertEqual(ins["data_sources"], ["calendar", "location"])

    def test_insights_custom_params(self):
        r = self.client.get(
            "/api/insights",
            params={"data_sources": "fit", "focus_areas": "health"},
        )
        ins = r.json()["result"]["insights"]
        self.assertEqual(ins["focus_areas"], ["health"])

    def test_daily_summary_returns_rating(self):
        r = self.client.get("/api/daily-summary", params={"date": "2026-04-25"})
        self.assertEqual(r.status_code, 200)
        s = r.json()["result"]["summary"]
        self.assertEqual(s["date"], "2026-04-25")
        self.assertIn(s["rating"], {"Excellent", "Good", "Low activity"})

    def test_habits_periods(self):
        for period in ("day", "week", "month"):
            r = self.client.get("/api/habits", params={"time_period": period})
            self.assertEqual(r.status_code, 200, period)
            h = r.json()["result"]["habits"]
            self.assertEqual(h["period"], period)
            self.assertIn("breakdown", h)

    def test_semantic_search_handles_empty_index(self):
        # Patch the lazy import path so we don't need a populated FAISS index.
        fake_results = [
            {"document": {"id": "doc1", "metadata": {"type": "calendar_event"}},
             "similarity_score": 0.42, "index": 0}
        ]

        class _Stub:
            def semantic_search(self, query, k=5, filters=None):
                return fake_results

        with patch.dict("sys.modules", {"ragsystem.mcp_integration": type(
            "M", (), {"rag_mcp_integrator": _Stub()}
        )}):
            r = self.client.get(
                "/api/semantic-search",
                params={"query": "meeting", "max_results": 3,
                        "data_filters": "calendar_event"},
            )
        self.assertEqual(r.status_code, 200)
        body = r.json()["result"]
        self.assertEqual(body["query"], "meeting")
        self.assertEqual(body["total_found"], 1)
        self.assertEqual(body["filters_applied"], ["type"])


if __name__ == "__main__":
    unittest.main()
