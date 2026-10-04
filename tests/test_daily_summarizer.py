import unittest
from ragsystem.daily_summarizer import DailySummarizer


class TestDailySummarizerTrends(unittest.TestCase):
    def test_identify_weekly_trends_activity_type_counting(self):
        summarizer = DailySummarizer()
        weekly_data = {
            "2026-03-01": {
                "location_summary": {
                    "location_types_visited": {"gym": 1, "work": 1}
                },
                "fitness_summary": {
                    "activities": [
                        {"type": "running", "duration": 30, "calories_burned": 300, "time": "10:00:00"},
                        {"type": "walking", "duration": 20, "calories_burned": 100, "time": "15:00:00"},
                    ],
                    "total_activities": 2,
                },
                "calendar_summary": {
                    "busyness_level": "Medium",
                    "total_events": 2,
                    "total_booked_hours": 3.0,
                },
            },
            "2026-03-02": {
                "location_summary": {
                    "location_types_visited": {"home": 1, "work": 1}
                },
                "fitness_summary": {
                    "activities": [
                        {"type": "running", "duration": 45, "calories_burned": 450, "time": "08:00:00"},
                    ],
                    "total_activities": 1,
                },
                "calendar_summary": {
                    "busyness_level": "High",
                    "total_events": 5,
                    "total_booked_hours": 6.0,
                },
            },
        }

        trends = summarizer._identify_weekly_trends(weekly_data)
        self.assertIn("top_activities", trends)
        # Running should be top activity with count 2, followed by walking with count 1
        top_activities_dict = dict(trends["top_activities"])
        self.assertEqual(top_activities_dict.get("running"), 2)
        self.assertEqual(top_activities_dict.get("walking"), 1)


if __name__ == "__main__":
    unittest.main()
