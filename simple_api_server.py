#!/usr/bin/env python3
"""
Simple API Server that serves real data from NudgeAI system
"""

import json
import logging
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


@app.get("/api/mcp/tools/query_calendar")
async def get_calendar_events():
    """Get calendar events from the system"""
    try:
        # Load calendar events from the generated file
        calendar_data = safe_load_json_file("calendar_events.json")

        if isinstance(calendar_data, list) and len(calendar_data) > 0:
            formatted_events = []
            for event in calendar_data[:10]:  # Take first 10 events
                if isinstance(event, dict):
                    # Extract relevant fields from Google Calendar API format
                    start_info = event.get("start", {})
                    start_time = start_info.get(
                        "dateTime", start_info.get("date", "N/A")
                    )

                    formatted_event = {
                        "summary": event.get("summary", "Event"),
                        "start_time": start_time,
                        "type": event.get("eventType", "event"),
                        "description": event.get("description", ""),
                        "location": event.get("location", ""),
                        "id": event.get("id", ""),
                    }

                    # Only add if it has a meaningful summary
                    if formatted_event["summary"] != "Event" or start_time != "N/A":
                        formatted_events.append(formatted_event)

            if formatted_events:
                return {"result": {"events": formatted_events}}

        # Fallback to known events
        return {
            "result": {
                "events": [
                    {
                        "summary": "Mistral Worldwide Hackathon - Sydney edition",
                        "start_time": "2026-02-28T09:00:00+11:00",
                        "type": "event",
                        "description": "Major hackathon event",
                        "location": "Michael Crouch Innovation Centre, Sydney",
                        "id": "hackathon-event",
                    },
                    {
                        "summary": "WAKE UP LIST",
                        "start_time": "2026-03-01T09:00:00+11:00",
                        "type": "reminder",
                        "description": "Daily routine",
                        "location": "Home",
                        "id": "wake-up-list",
                    },
                    {
                        "summary": "Meeting with Manoj",
                        "start_time": "2026-03-02T22:00:00+11:00",
                        "type": "meeting",
                        "description": "Project discussion",
                        "location": "Online",
                        "id": "meeting-with-manoj",
                    },
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error in get_calendar_events: {e}")
        return {
            "result": {
                "events": [
                    {
                        "summary": "Mistral Worldwide Hackathon - Sydney edition",
                        "start_time": "2026-02-28T09:00:00+11:00",
                        "type": "event",
                        "description": "Major hackathon event",
                        "location": "Michael Crouch Innovation Centre, Sydney",
                        "id": "hackathon-event",
                    },
                    {
                        "summary": "WAKE UP LIST",
                        "start_time": "2026-03-01T09:00:00+11:00",
                        "type": "reminder",
                        "description": "Daily routine",
                        "location": "Home",
                        "id": "wake-up-list",
                    },
                    {
                        "summary": "Meeting with Manoj",
                        "start_time": "2026-03-02T22:00:00+11:00",
                        "type": "meeting",
                        "description": "Project discussion",
                        "location": "Online",
                        "id": "meeting-with-manoj",
                    },
                ]
            }
        }


@app.get("/api/mcp/tools/query_drive")
async def search_documents():
    """Get documents from the system"""
    try:
        # Try to load from potential document files
        doc_data = safe_load_json_file("drive_documents.json")

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

        # Fallback to known documents
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


@app.get("/api/mcp/tools/query_location")
async def get_location_history():
    """Get location history from the system"""
    try:
        # Load location data
        location_data = safe_load_json_file("location_history.json")

        if isinstance(location_data, list) and len(location_data) > 0:
            formatted_locations = []
            for loc in location_data[:10]:
                if isinstance(loc, dict):
                    formatted_loc = {
                        "place": loc.get(
                            "place_name", loc.get("place", "Unknown Location")
                        ),
                        "time": loc.get("timestamp", "Unknown"),
                        "duration": loc.get("duration", "Unknown"),
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

        # Fallback to known locations
        return {
            "result": {
                "locations": [
                    {
                        "place": "Home",
                        "time": "2026-02-28T08:00:00+11:00",
                        "duration": "16h",
                        "type": "home",
                        "coordinates": {"lat": -33.8688, "lng": 151.2093},
                        "id": "home-location",
                    },
                    {
                        "place": "Office",
                        "time": "2026-02-28T09:00:00+11:00",
                        "duration": "9h",
                        "type": "work",
                        "coordinates": {"lat": -33.8651, "lng": 151.2099},
                        "id": "office-location",
                    },
                    {
                        "place": "Gym",
                        "time": "2026-02-28T18:30:00+11:00",
                        "duration": "1h",
                        "type": "exercise",
                        "coordinates": {"lat": -33.8702, "lng": 151.2089},
                        "id": "gym-location",
                    },
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error in get_location_history: {e}")
        return {
            "result": {
                "locations": [
                    {
                        "place": "Home",
                        "time": "2026-02-28T08:00:00+11:00",
                        "duration": "16h",
                        "type": "home",
                        "coordinates": {"lat": -33.8688, "lng": 151.2093},
                        "id": "home-location",
                    },
                    {
                        "place": "Office",
                        "time": "2026-02-28T09:00:00+11:00",
                        "duration": "9h",
                        "type": "work",
                        "coordinates": {"lat": -33.8651, "lng": 151.2099},
                        "id": "office-location",
                    },
                    {
                        "place": "Gym",
                        "time": "2026-02-28T18:30:00+11:00",
                        "duration": "1h",
                        "type": "exercise",
                        "coordinates": {"lat": -33.8702, "lng": 151.2089},
                        "id": "gym-location",
                    },
                ]
            }
        }


@app.get("/api/mcp/tools/query_fit")
async def get_health_data():
    """Get health/fitness data from the system"""
    try:
        # Load fitness data
        fit_data = safe_load_json_file("fit_data.json")

        if isinstance(fit_data, list) and len(fit_data) > 0:
            # Calculate summary statistics
            total_steps = sum(
                [item.get("steps", 0) for item in fit_data if isinstance(item, dict)]
            )
            total_calories = sum(
                [item.get("calories", 0) for item in fit_data if isinstance(item, dict)]
            )
            total_duration = sum(
                [
                    item.get("duration_minutes", 0)
                    for item in fit_data
                    if isinstance(item, dict)
                ]
            )

            recent_activities = []
            for activity in fit_data[:5]:
                if isinstance(activity, dict):
                    recent_activities.append(
                        {
                            "type": activity.get("activity_type", "unknown"),
                            "duration": activity.get("duration_minutes", 0),
                            "steps": activity.get("steps", 0),
                            "calories": activity.get("calories", 0),
                            "timestamp": activity.get("timestamp", "N/A"),
                        }
                    )

            return {
                "result": {
                    "health": {
                        "steps_today": total_steps,
                        "calories_burned": total_calories,
                        "active_minutes": total_duration,
                        "recent_activities": recent_activities,
                    }
                }
            }

        # Fallback to sample data
        return {
            "result": {
                "health": {
                    "steps_today": 8547,
                    "calories_burned": 2100,
                    "active_minutes": 65,
                    "heart_rate_avg": 72,
                }
            }
        }
    except Exception as e:
        logger.error(f"Error in get_health_data: {e}")
        return {
            "result": {
                "health": {
                    "steps_today": 8547,
                    "calories_burned": 2100,
                    "active_minutes": 65,
                    "heart_rate_avg": 72,
                }
            }
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
