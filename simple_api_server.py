#!/usr/bin/env python3
"""
Simple API Server that serves real data from NudgeAI system
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NudgeAI Simple Data API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


def safe_load_json_file(filename):
    """Safely load JSON file with error handling"""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"File {filename} not found")
        return []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in {filename}")
        return []
    except Exception as e:
        logger.error(f"Error reading {filename}: {e}")
        return []


def parse_duration_hours(duration_str: str) -> float:
    """Convert duration string like '16h', '1h', '30m' to float hours."""
    if not duration_str or duration_str in ("Unknown", "N/A"):
        return 0.0
    s = str(duration_str).strip().lower()
    if "h" in s and "m" in s:
        parts = s.replace("m", "").split("h")
        return float(parts[0]) + float(parts[1]) / 60
    if s.endswith("h"):
        return float(s[:-1])
    if s.endswith("m"):
        return float(s[:-1]) / 60
    try:
        return float(s)
    except ValueError:
        return 0.0


@app.get("/api/mcp/tools/query_calendar")
@app.get("/api/calendar")
async def get_calendar_events():
    """Get calendar events from the system"""
    try:
        calendar_data = safe_load_json_file("data_sync/calendar_sync.json")

        if isinstance(calendar_data, list) and len(calendar_data) > 0:
            formatted_events = []
            for event in calendar_data[:10]:
                if isinstance(event, dict):
                    start_info = event.get("start", {})
                    end_info = event.get("end", {})
                    start_time = start_info.get(
                        "dateTime", start_info.get("date", "N/A")
                    )
                    end_time = end_info.get("dateTime", end_info.get("date", ""))
                    attendees = [
                        a.get("email", a.get("displayName", ""))
                        for a in event.get("attendees", [])
                    ]

                    formatted_event = {
                        "summary": event.get("summary", "Event"),
                        "start_time": start_time,
                        "end_time": end_time,
                        "type": event.get("eventType", "event"),
                        "description": event.get("description", ""),
                        "location": event.get("location", ""),
                        "attendees": attendees,
                        "id": event.get("id", ""),
                    }

                    if formatted_event["summary"] != "Event" or start_time != "N/A":
                        formatted_events.append(formatted_event)

            if formatted_events:
                return {"result": {"events": formatted_events}}

        # Fallback to known events
        fallback_events = [
            {
                "summary": "Mistral Worldwide Hackathon - Sydney edition",
                "start_time": "2026-02-28T09:00:00+11:00",
                "end_time": "2026-02-28T18:00:00+11:00",
                "type": "event",
                "description": "Major hackathon event",
                "location": "Michael Crouch Innovation Centre, Sydney",
                "attendees": [],
                "id": "hackathon-event",
            },
            {
                "summary": "WAKE UP LIST",
                "start_time": "2026-03-01T09:00:00+11:00",
                "end_time": "2026-03-01T09:30:00+11:00",
                "type": "reminder",
                "description": "Daily routine",
                "location": "Home",
                "attendees": [],
                "id": "wake-up-list",
            },
            {
                "summary": "Meeting with Manoj",
                "start_time": "2026-03-02T22:00:00+11:00",
                "end_time": "2026-03-02T23:00:00+11:00",
                "type": "meeting",
                "description": "Project discussion",
                "location": "Online",
                "attendees": ["manoj@example.com"],
                "id": "meeting-with-manoj",
            },
        ]
        return {"result": {"events": fallback_events}}

    except Exception as e:
        logger.error(f"Error in get_calendar_events: {e}")
        return {"result": {"events": []}}


@app.get("/api/mcp/tools/query_drive")
@app.get("/api/drive")
async def search_documents():
    """Get documents from the system"""
    try:
        doc_data = safe_load_json_file("data_sync/drive_sync.json")

        if isinstance(doc_data, list) and len(doc_data) > 0:
            formatted_docs = []
            for doc in doc_data[:10]:
                if isinstance(doc, dict):
                    formatted_doc = {
                        "title": doc.get("name", doc.get("title", "Untitled Document")),
                        "url": doc.get("webViewLink", doc.get("url", "#")),
                        "modified": doc.get("modifiedTime", "Unknown"),
                        "type": doc.get("mimeType", "document"),
                        "id": doc.get("id", ""),
                    }
                    formatted_docs.append(formatted_doc)

            if formatted_docs:
                return {"result": {"documents": formatted_docs}}

        # Fallback
        return {
            "result": {
                "documents": [
                    {
                        "title": "Marketing Budget 2024.xlsx",
                        "url": "https://drive.google.com/file/d/...",
                        "modified": "2026-02-27T14:30:00Z",
                        "type": "spreadsheet",
                        "id": "budget-sheet",
                    },
                    {
                        "title": "Project Plan.docx",
                        "url": "https://drive.google.com/file/d/...",
                        "modified": "2026-02-26T10:15:00Z",
                        "type": "document",
                        "id": "project-plan",
                    },
                    {
                        "title": "Meeting Notes.pdf",
                        "url": "https://drive.google.com/file/d/...",
                        "modified": "2026-02-25T16:45:00Z",
                        "type": "pdf",
                        "id": "meeting-notes",
                    },
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error in search_documents: {e}")
        return {"result": {"documents": []}}


@app.get("/api/mcp/tools/query_location")
@app.get("/api/location")
async def get_location_history():
    """Get location history from the system"""
    try:
        location_data = safe_load_json_file("data_sync/location_sync.json")

        if isinstance(location_data, list) and len(location_data) > 0:
            formatted_locations = []
            for loc in location_data[:10]:
                if isinstance(loc, dict):
                    duration_str = loc.get("duration", "Unknown")
                    formatted_loc = {
                        "place": loc.get(
                            "place_name", loc.get("place", "Unknown Location")
                        ),
                        "time": loc.get("timestamp", "Unknown"),
                        "duration": duration_str,
                        "duration_hours": parse_duration_hours(duration_str),
                        "type": loc.get("location_type", "location"),
                        "coordinates": {
                            "lat": loc.get("latitude", 0),
                            "lng": loc.get("longitude", 0),
                        },
                        "id": loc.get("id", ""),
                    }
                    formatted_locations.append(formatted_loc)

            if formatted_locations:
                return {"result": {"locations": formatted_locations}}

        # Fallback
        fallback_locations = [
            {
                "place": "Home",
                "time": "2026-02-28T08:00:00+11:00",
                "duration": "16h",
                "duration_hours": 16.0,
                "type": "home",
                "coordinates": {"lat": -33.8688, "lng": 151.2093},
                "id": "home-location",
            },
            {
                "place": "Office",
                "time": "2026-02-28T09:00:00+11:00",
                "duration": "9h",
                "duration_hours": 9.0,
                "type": "work",
                "coordinates": {"lat": -33.8651, "lng": 151.2099},
                "id": "office-location",
            },
            {
                "place": "Gym",
                "time": "2026-02-28T18:30:00+11:00",
                "duration": "1h",
                "duration_hours": 1.0,
                "type": "exercise",
                "coordinates": {"lat": -33.8702, "lng": 151.2089},
                "id": "gym-location",
            },
        ]
        return {"result": {"locations": fallback_locations}}

    except Exception as e:
        logger.error(f"Error in get_location_history: {e}")
        return {"result": {"locations": []}}


@app.get("/api/mcp/tools/query_fit")
@app.get("/api/fit")
async def get_health_data():
    """Get health/fitness data from the system"""
    try:
        fit_data = safe_load_json_file("data_sync/fit_sync.json")

        if isinstance(fit_data, list) and len(fit_data) > 0:
            # Aggregate daily steps/calories for the last 7 days
            today = datetime.utcnow().date()
            daily_steps = defaultdict(int)
            daily_calories = defaultdict(int)

            total_steps = 0
            total_calories = 0
            total_duration = 0
            recent_activities = []

            for item in fit_data:
                if not isinstance(item, dict):
                    continue
                steps = item.get("steps", 0)
                calories = item.get("calories", 0)
                duration = item.get("duration_minutes", 0)
                total_steps += steps
                total_calories += calories
                total_duration += duration

                # Bucket into day offset for weekly arrays
                ts_raw = item.get("timestamp", "")
                try:
                    ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                    day_offset = (today - ts.date()).days
                    if 0 <= day_offset < 7:
                        daily_steps[day_offset] += steps
                        daily_calories[day_offset] += calories
                except Exception:
                    pass

                if len(recent_activities) < 5:
                    recent_activities.append(
                        {
                            "type": item.get("activity_type", "unknown"),
                            "duration": duration,
                            "steps": steps,
                            "calories": calories,
                            "timestamp": ts_raw,
                        }
                    )

            # Build 7-element arrays (index 0 = today, 6 = 6 days ago)
            # Chart wants Mon→Sun order so reverse
            weekly_steps = [daily_steps.get(i, 0) for i in range(6, -1, -1)]
            weekly_calories = [daily_calories.get(i, 0) for i in range(6, -1, -1)]

            return {
                "result": {
                    "health": {
                        "steps_today": daily_steps.get(0, total_steps),
                        "calories_burned": daily_calories.get(0, total_calories),
                        "active_minutes": total_duration,
                        "weekly_steps": weekly_steps,
                        "weekly_calories": weekly_calories,
                        "recent_activities": recent_activities,
                    }
                }
            }

        # Fallback
        return {
            "result": {
                "health": {
                    "steps_today": 8547,
                    "calories_burned": 2100,
                    "active_minutes": 65,
                    "weekly_steps": [7200, 8547, 6800, 9200, 7800, 8100, 7500],
                    "weekly_calories": [1900, 2100, 1800, 2300, 2000, 2150, 1950],
                    "recent_activities": [
                        {
                            "type": "running",
                            "duration": 30,
                            "steps": 4500,
                            "calories": 380,
                            "timestamp": "2026-03-04T07:00:00Z",
                        },
                        {
                            "type": "walking",
                            "duration": 20,
                            "steps": 2000,
                            "calories": 120,
                            "timestamp": "2026-03-03T12:00:00Z",
                        },
                    ],
                }
            }
        }
    except Exception as e:
        logger.error(f"Error in get_health_data: {e}")
        return {
            "result": {
                "health": {
                    "steps_today": 0,
                    "calories_burned": 0,
                    "active_minutes": 0,
                    "weekly_steps": [0] * 7,
                    "weekly_calories": [0] * 7,
                    "recent_activities": [],
                }
            }
        }


@app.get("/api/insights")
async def get_insights(
    data_sources: str = "calendar,location", focus_areas: str = "productivity,health"
):
    """Generate personal insights from available data"""
    try:
        sources = [s.strip() for s in data_sources.split(",")]
        areas = [a.strip() for a in focus_areas.split(",")]

        fit_data = safe_load_json_file("data_sync/fit_sync.json")
        location_data = safe_load_json_file("data_sync/location_sync.json")
        calendar_data = safe_load_json_file("data_sync/calendar_sync.json")

        total_steps = sum(
            item.get("steps", 0) for item in fit_data if isinstance(item, dict)
        )
        total_activities = len(fit_data) if isinstance(fit_data, list) else 0
        total_locations = len(location_data) if isinstance(location_data, list) else 0
        total_events = len(calendar_data) if isinstance(calendar_data, list) else 0

        patterns = []
        recommendations = []

        if "health" in areas or "fitness" in areas:
            avg_steps = total_steps // max(total_activities, 1)
            if avg_steps > 7500:
                patterns.append(
                    f"You are averaging {avg_steps:,} steps per activity — above the 7,500 daily target."
                )
            else:
                patterns.append(
                    f"Your average step count ({avg_steps:,}) is below the 7,500 daily target."
                )
                recommendations.append(
                    "Try to add a 20-minute walk each day to boost your step count."
                )

        if "productivity" in areas:
            patterns.append(f"You have {total_events} calendar events in the system.")
            if total_events < 3:
                recommendations.append(
                    "Consider blocking focus time on your calendar for deep work."
                )

        if "location" in areas:
            patterns.append(
                f"Location history shows {total_locations} recorded visits."
            )

        return {
            "result": {
                "insights": {
                    "data_sources": sources,
                    "focus_areas": areas,
                    "patterns": patterns or ["Not enough data to detect patterns yet."],
                    "recommendations": recommendations
                    or ["Keep syncing your data for personalised recommendations."],
                    "summary": f"Analysed {total_activities} fitness activities, {total_events} calendar events, and {total_locations} location visits.",
                }
            }
        }

    except Exception as e:
        logger.error(f"Error in get_insights: {e}")
        return {
            "result": {
                "insights": {
                    "patterns": ["Unable to load insights."],
                    "recommendations": [],
                    "summary": "Data unavailable.",
                }
            }
        }


@app.get("/api/daily-summary")
async def get_daily_summary(date: str = None):
    """Generate a daily summary for a given date"""
    try:
        target_date = date or datetime.utcnow().strftime("%Y-%m-%d")

        fit_data = safe_load_json_file("data_sync/fit_sync.json")
        calendar_data = safe_load_json_file("data_sync/calendar_sync.json")
        location_data = safe_load_json_file("data_sync/location_sync.json")

        # Filter to target date
        def on_date(ts_str, target):
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                return ts.strftime("%Y-%m-%d") == target
            except Exception:
                return False

        day_activities = [
            item
            for item in (fit_data if isinstance(fit_data, list) else [])
            if isinstance(item, dict)
            and on_date(item.get("timestamp", ""), target_date)
        ]
        day_events = [
            ev
            for ev in (calendar_data if isinstance(calendar_data, list) else [])
            if isinstance(ev, dict)
            and on_date(
                ev.get("start", {}).get(
                    "dateTime", ev.get("start", {}).get("date", "")
                ),
                target_date,
            )
        ]
        day_locations = [
            loc
            for loc in (location_data if isinstance(location_data, list) else [])
            if isinstance(loc, dict) and on_date(loc.get("timestamp", ""), target_date)
        ]

        steps = sum(a.get("steps", 0) for a in day_activities)
        calories = sum(a.get("calories", 0) for a in day_activities)
        active_min = sum(a.get("duration_minutes", 0) for a in day_activities)

        rating = "Good"
        if steps > 10000:
            rating = "Excellent"
        elif steps < 3000 and len(day_activities) == 0:
            rating = "Low activity"

        return {
            "result": {
                "summary": {
                    "date": target_date,
                    "rating": rating,
                    "details": {
                        "fitness": {
                            "activities": len(day_activities),
                            "steps": steps,
                            "calories": calories,
                            "active_minutes": active_min,
                        },
                        "calendar": {
                            "events": len(day_events),
                            "titles": [
                                ev.get("summary", "Untitled") for ev in day_events[:5]
                            ],
                        },
                        "location": {
                            "visits": len(day_locations),
                            "places": [
                                loc.get("place_name", loc.get("place", ""))
                                for loc in day_locations[:5]
                            ],
                        },
                    },
                    "recommendations": [
                        "Great work staying active today!"
                        if steps > 7500
                        else "Try to add a short walk tomorrow.",
                    ],
                }
            }
        }

    except Exception as e:
        logger.error(f"Error in get_daily_summary: {e}")
        return {
            "result": {
                "summary": {
                    "date": date,
                    "rating": "Unknown",
                    "details": {},
                    "recommendations": [],
                }
            }
        }


@app.get("/api/habits")
async def get_habits(time_period: str = "week", focus_area: str = ""):
    """Analyse habit patterns over a time period"""
    try:
        period_days = {"day": 1, "week": 7, "month": 30}.get(time_period, 7)
        cutoff = datetime.utcnow() - timedelta(days=period_days)

        fit_data = safe_load_json_file("data_sync/fit_sync.json")

        def recent(ts_str):
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).replace(
                    tzinfo=None
                )
                return ts >= cutoff
            except Exception:
                return False

        activities = [
            item
            for item in (fit_data if isinstance(fit_data, list) else [])
            if isinstance(item, dict) and recent(item.get("timestamp", ""))
        ]

        activity_counts = defaultdict(int)
        for a in activities:
            activity_counts[a.get("activity_type", "unknown")] += 1

        habits = [
            {
                "activity": act,
                "count": count,
                "frequency": f"{count}x per {time_period}",
            }
            for act, count in sorted(activity_counts.items(), key=lambda x: -x[1])
        ]

        return {
            "result": {
                "habits": {
                    "period": time_period,
                    "focus_area": focus_area or "all",
                    "total_activities": len(activities),
                    "breakdown": habits,
                    "consistency_score": min(100, len(activities) * 10),
                }
            }
        }

    except Exception as e:
        logger.error(f"Error in get_habits: {e}")
        return {
            "result": {
                "habits": {
                    "period": time_period,
                    "total_activities": 0,
                    "breakdown": [],
                }
            }
        }


@app.get("/api/semantic-search")
async def semantic_search(query: str, data_filters: str = None, max_results: int = 5):
    """Semantic search across indexed RAG data."""
    try:
        from ragsystem.mcp_integration import rag_mcp_integrator

        filters = None
        if data_filters:
            types = [s.strip() for s in data_filters.split(",") if s.strip()]
            if types:
                filters = {"type": types}

        results = rag_mcp_integrator.semantic_search(
            query, k=max_results, filters=filters
        )
        return {
            "result": {
                "query": query,
                "results": results,
                "total_found": len(results),
                "filters_applied": list(filters.keys()) if filters else [],
            }
        }
    except Exception as e:
        logger.error(f"Error in semantic_search: {e}")
        return {
            "result": {
                "query": query,
                "results": [],
                "total_found": 0,
                "filters_applied": [],
                "error": str(e),
            }
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
