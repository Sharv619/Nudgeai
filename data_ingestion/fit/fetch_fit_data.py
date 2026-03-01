#!/usr/bin/env python3
"""
Simulate Google Fit data for demo purposes.
In a real implementation, this would connect to Google Fit API.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict


def generate_mock_fit_data(days: int = 7) -> List[Dict]:
    """
    Generate realistic fitness data for demo purposes.
    """
    activities = []

    for day_offset in range(days):
        base_date = datetime.now() - timedelta(days=day_offset)

        # Determine if this day has activity based on patterns
        is_weekday = base_date.weekday() < 5  # Mon-Fri

        # More exercise on certain days of the week
        exercise_probability = (
            0.7 if day_offset % 7 in [0, 2, 4, 6] else 0.4
        )  # More active on Sun, Tue, Thu, Sat
        walk_probability = 0.8  # Most days have walking

        # Walking activity (daily)
        if random.random() < walk_probability:
            walk_start = datetime.combine(
                base_date.date(), datetime.min.time()
            ) + timedelta(hours=12, minutes=random.randint(0, 59))  # Mid-day walk
            duration = random.randint(15, 45)  # 15-45 minutes
            steps = random.randint(2000, 8000)  # Average walk steps
            calories = int(steps * 0.04)  # Approximate calories burned

            activities.append(
                {
                    "id": f"fit_walk_{walk_start.strftime('%Y%m%d_%H%M%S')}",
                    "timestamp": walk_start.isoformat() + "Z",
                    "activity_type": "walking",
                    "duration_minutes": duration,
                    "steps": steps,
                    "calories": calories,
                    "distance_meters": int(steps * 0.8),  # Approximate distance
                }
            )

        # Exercise activity (based on pattern)
        if random.random() < exercise_probability:
            exercise_start = datetime.combine(
                base_date.date(), datetime.min.time()
            ) + timedelta(
                hours=random.randint(6, 9), minutes=random.randint(0, 59)
            )  # Morning exercise
            exercise_types = [
                "running",
                "cycling",
                "swimming",
                "gym",
                "yoga",
                "strength_training",
            ]
            activity_type = random.choice(exercise_types)

            if activity_type in ["running", "cycling"]:
                duration = random.randint(30, 90)
                steps = random.randint(5000, 15000) if activity_type == "running" else 0
                calories = random.randint(300, 600)
                distance_meters = int(random.randint(3000, 10000))
            elif activity_type in ["swimming", "gym", "strength_training"]:
                duration = random.randint(45, 120)
                steps = 0  # Indoor activities
                calories = random.randint(250, 500)
                distance_meters = 0
            else:  # yoga
                duration = random.randint(30, 60)
                steps = random.randint(1000, 3000)
                calories = random.randint(150, 300)
                distance_meters = int(steps * 0.8)

            activities.append(
                {
                    "id": f"fit_ex_{activity_type}_{exercise_start.strftime('%Y%m%d_%H%M%S')}",
                    "timestamp": exercise_start.isoformat() + "Z",
                    "activity_type": activity_type,
                    "duration_minutes": duration,
                    "steps": steps,
                    "calories": calories,
                    "distance_meters": distance_meters,
                }
            )

    return activities


def save_fit_data(activities: List[Dict], filename="fit_data.json"):
    """
    Save fitness data to a JSON file.
    """
    with open(filename, "w") as f:
        json.dump(activities, f, indent=2)
    print(f"Fitness data saved to {filename}")


def format_fit_for_rag(activities: List[Dict]) -> List[Dict]:
    """
    Format fitness data for RAG system with consistent structure.
    """
    formatted_activities = []
    for activity in activities:
        formatted_activity = {
            "id": activity["id"],
            "text": f"{activity['activity_type']} for {activity['duration_minutes']} minutes "
            f"burning {activity['calories']} calories on {activity['timestamp']}",
            "metadata": {
                "type": "fitness_activity",
                "activity_type": activity["activity_type"],
                "timestamp": activity["timestamp"],
                "duration_minutes": activity["duration_minutes"],
                "steps": activity["steps"],
                "calories": activity["calories"],
                "distance_meters": activity["distance_meters"],
            },
        }
        formatted_activities.append(formatted_activity)

    return formatted_activities


def main():
    """
    Main function to generate and save fitness data.
    """
    print("Generating mock Google Fit data for demo...")
    activities = generate_mock_fit_data(days=7)
    save_fit_data(activities)

    # Format for RAG system
    rag_formatted = format_fit_for_rag(activities)
    with open("fit_data_rag.json", "w") as f:
        json.dump(rag_formatted, f, indent=2)
    print(f"Formatted {len(rag_formatted)} fitness records for RAG system")


if __name__ == "__main__":
    main()
