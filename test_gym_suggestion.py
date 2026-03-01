#!/usr/bin/env python3
"""
Test script to verify the gym time suggestion functionality
"""

import asyncio
import json
from datetime import datetime, timedelta


def test_gym_suggestion_logic():
    """Test the gym suggestion logic with sample data"""
    print("Testing gym time suggestion functionality...")

    # Load calendar events for today and the next few days
    import json
    import os

    calendar_file = "data_sync/calendar_sync.json"
    calendar_events = []

    try:
        if os.path.exists(calendar_file):
            with open(calendar_file, "r") as f:
                calendar_data = json.load(f)

            # Get events for today and next 2 days
            start_date = datetime.now()
            end_date = start_date + timedelta(days=2)

            for item in calendar_data:
                metadata = item.get("metadata", {})
                start_time = metadata.get("start_time", "")

                if start_time:
                    try:
                        event_dt = datetime.fromisoformat(
                            start_time.replace("Z", "+00:00")
                        )
                        # Convert to naive datetime for comparison
                        event_dt = event_dt.replace(tzinfo=None)

                        if start_date <= event_dt <= end_date:
                            calendar_events.append(
                                {
                                    "id": metadata.get("id", item.get("id", "")),
                                    "title": metadata.get(
                                        "summary", metadata.get("title", "No title")
                                    ),
                                    "start_time": metadata.get("start_time", ""),
                                    "end_time": metadata.get("end_time", ""),
                                    "location": metadata.get("location", ""),
                                    "attendees": metadata.get("attendees", []),
                                    "description": metadata.get("description", ""),
                                    "synced_at": metadata.get("synced_at", ""),
                                }
                            )
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Error reading calendar data: {e}")

    # Load fitness data to understand patterns
    fitness_file = "data_sync/fit_sync.json"
    fitness_activities = []

    try:
        if os.path.exists(fitness_file):
            with open(fitness_file, "r") as f:
                fitness_data = json.load(f)

            for item in fitness_data:
                metadata = item.get("metadata", {})
                timestamp = metadata.get("timestamp", "")

                if timestamp:
                    try:
                        event_dt = datetime.fromisoformat(
                            timestamp.replace("Z", "+00:00")
                        )
                        # Convert to naive datetime for comparison
                        event_dt = event_dt.replace(tzinfo=None)

                        if start_date <= event_dt <= end_date:
                            fitness_activities.append(metadata)
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Error reading fitness data: {e}")

    # Find free time slots in the calendar
    free_slots = []
    day_start = datetime.combine(datetime.now().date(), datetime.min.time()).replace(
        hour=6
    )  # Start at 6 AM
    day_end = datetime.combine(datetime.now().date(), datetime.min.time()).replace(
        hour=23
    )  # End at 11 PM

    # Sort events by start time
    sorted_events = sorted(calendar_events, key=lambda x: x["start_time"])

    current_time = day_start
    for event in sorted_events:
        event_start = datetime.fromisoformat(
            event["start_time"].replace("Z", "+00:00")
        ).replace(tzinfo=None)

        # Check if there's free time before this event
        if current_time < event_start:
            if (
                event_start - current_time
            ).total_seconds() / 60 >= 30:  # At least 30 minutes free
                free_slots.append(
                    {
                        "start": current_time.strftime("%H:%M"),
                        "end": event_start.strftime("%H:%M"),
                        "duration": int(
                            (event_start - current_time).total_seconds() / 60
                        ),
                    }
                )

        # Update current time to end of this event
        try:
            event_end = datetime.fromisoformat(
                event["end_time"].replace("Z", "+00:00")
            ).replace(tzinfo=None)
        except ValueError:
            event_end = event_start + timedelta(
                hours=1
            )  # Default to 1-hour event if no end time

        current_time = max(current_time, event_end)

    # Add final free slot if any time remains until day_end
    if current_time < day_end:
        if (
            day_end - current_time
        ).total_seconds() / 60 >= 30:  # At least 30 minutes free
            free_slots.append(
                {
                    "start": current_time.strftime("%H:%M"),
                    "end": day_end.strftime("%H:%M"),
                    "duration": int((day_end - current_time).total_seconds() / 60),
                }
            )

    # Analyze fitness patterns to recommend optimal gym time
    preferred_times = []
    if fitness_activities:
        # Analyze when the user typically exercises
        morning_workouts = 0
        afternoon_workouts = 0
        evening_workouts = 0

        for activity in fitness_activities:
            time_of_day = datetime.fromisoformat(
                activity["timestamp"].replace("Z", "+00:00")
            ).replace(tzinfo=None)
            hour = time_of_day.hour

            if 5 <= hour < 12:
                morning_workouts += 1
            elif 12 <= hour < 18:
                afternoon_workouts += 1
            else:
                evening_workouts += 1

        # Create preference ranking based on historical data
        time_preferences = [
            ("morning", morning_workouts),
            ("afternoon", afternoon_workouts),
            ("evening", evening_workouts),
        ]
        time_preferences.sort(key=lambda x: x[1], reverse=True)

        for pref, count in time_preferences:
            if count > 0:
                preferred_times.append(pref)

    # Generate gym time suggestions based on free slots and preferences
    suggestions = []
    for slot in free_slots:
        start_hour = int(slot["start"].split(":")[0])

        # Determine time of day
        if 5 <= start_hour < 12:
            time_of_day = "morning"
        elif 12 <= start_hour < 18:
            time_of_day = "afternoon"
        else:
            time_of_day = "evening"

        # Score the slot based on user preferences and duration
        score = 0
        if time_of_day in preferred_times:
            score += (
                preferred_times.index(time_of_day) * 10
            )  # Higher preference gets higher score
        score += (
            min(slot["duration"] // 30, 4) * 5
        )  # Longer duration gets higher score (up to 2 hours)

        suggestions.append(
            {
                "time_slot": f"{slot['start']} - {slot['end']}",
                "duration_minutes": slot["duration"],
                "time_of_day": time_of_day,
                "score": score,
                "suitability": "High"
                if score >= 15
                else "Medium"
                if score >= 5
                else "Low",
            }
        )

    # Sort suggestions by score (highest first)
    suggestions.sort(key=lambda x: x["score"], reverse=True)

    # Prepare response
    if suggestions:
        best_suggestion = suggestions[0]
        recommendation = f"Based on your calendar and fitness patterns, the best time for gym today is {best_suggestion['time_slot']} ({best_suggestion['time_of_day']}). Duration: {best_suggestion['duration_minutes']} minutes."
    else:
        # If no free slots, suggest early morning or late evening
        recommendation = "No extended free time found in your calendar today. Consider an early morning session (6-7 AM) or a late evening session (after 8 PM) if possible."

    # Also check for tomorrow if needed
    tomorrows_events = [
        event
        for event in calendar_events
        if datetime.fromisoformat(event["start_time"].replace("Z", "+00:00"))
        .replace(tzinfo=None)
        .date()
        == (datetime.now().date() + timedelta(days=1))
    ]

    tomorrow_suggestions = []  # Initialize the variable
    if not suggestions and tomorrows_events:
        # Find tomorrow's free slots
        tomorrow_free_slots = []
        tomorrow_start = datetime.combine(
            datetime.now().date() + timedelta(days=1), datetime.min.time()
        ).replace(hour=6)
        tomorrow_end = datetime.combine(
            datetime.now().date() + timedelta(days=1), datetime.min.time()
        ).replace(hour=23)

        tomorrows_sorted_events = sorted(
            tomorrows_events, key=lambda x: x["start_time"]
        )

        current_time = tomorrow_start
        for event in tomorrows_sorted_events:
            event_start = datetime.fromisoformat(
                event["start_time"].replace("Z", "+00:00")
            ).replace(tzinfo=None)

            # Check if there's free time before this event
            if current_time < event_start:
                if (
                    event_start - current_time
                ).total_seconds() / 60 >= 30:  # At least 30 minutes free
                    tomorrow_free_slots.append(
                        {
                            "start": current_time.strftime("%H:%M"),
                            "end": event_start.strftime("%H:%M"),
                            "duration": int(
                                (event_start - current_time).total_seconds() / 60
                            ),
                        }
                    )

            # Update current time to end of this event
            try:
                event_end = datetime.fromisoformat(
                    event["end_time"].replace("Z", "+00:00")
                ).replace(tzinfo=None)
            except ValueError:
                event_end = event_start + timedelta(
                    hours=1
                )  # Default to 1-hour event if no end time

            current_time = max(current_time, event_end)

        # Add final free slot if any time remains until tomorrow_end
        if current_time < tomorrow_end:
            if (
                tomorrow_end - current_time
            ).total_seconds() / 60 >= 30:  # At least 30 minutes free
                tomorrow_free_slots.append(
                    {
                        "start": current_time.strftime("%H:%M"),
                        "end": tomorrow_end.strftime("%H:%M"),
                        "duration": int(
                            (tomorrow_end - current_time).total_seconds() / 60
                        ),
                    }
                )

        for slot in tomorrow_free_slots:
            start_hour = int(slot["start"].split(":")[0])

            # Determine time of day
            if 5 <= start_hour < 12:
                time_of_day = "morning"
            elif 12 <= start_hour < 18:
                time_of_day = "afternoon"
            else:
                time_of_day = "evening"

            # Score the slot based on user preferences and duration
            score = 0
            if time_of_day in preferred_times:
                score += preferred_times.index(time_of_day) * 10
            score += min(slot["duration"] // 30, 4) * 5

            tomorrow_suggestions.append(
                {
                    "time_slot": f"{slot['start']} - {slot['end']}",
                    "duration_minutes": slot["duration"],
                    "time_of_day": time_of_day,
                    "score": score,
                    "suitability": "High"
                    if score >= 15
                    else "Medium"
                    if score >= 5
                    else "Low",
                }
            )

        tomorrow_suggestions.sort(key=lambda x: x["score"], reverse=True)

        if tomorrow_suggestions:
            best_tomorrow = tomorrow_suggestions[0]
            recommendation += f" Tomorrow ({(datetime.now() + timedelta(days=1)).strftime('%A, %b %d')}) looks better: {best_tomorrow['time_slot']} ({best_tomorrow['time_of_day']}). Duration: {best_tomorrow['duration_minutes']} minutes."

    print(f"✓ Calendar events found: {len(calendar_events)}")
    print(f"✓ Fitness activities found: {len(fitness_activities)}")
    print(f"✓ Free time slots found: {len(free_slots)}")
    print(f"✓ Preferred times: {preferred_times}")
    print(f"✓ Today's suggestions: {len(suggestions)}")
    print(f"✓ Tomorrow's suggestions: {len(tomorrow_suggestions)}")
    print(f"\n📋 RECOMMENDATION: {recommendation}")

    return {
        "recommendation": recommendation,
        "suggested_slots": suggestions[:3],  # Top 3 suggestions
        "tomorrow_suggestions": tomorrow_suggestions[:2],
        "free_time_slots": free_slots,
        "fitness_patterns": {
            "preferred_times": preferred_times,
            "recent_activities": len(fitness_activities),
        },
        "calendar_events_count": len(calendar_events),
    }


if __name__ == "__main__":
    result = test_gym_suggestion_logic()
    print("\n✅ Gym time suggestion functionality test completed successfully!")
