#!/usr/bin/env python3
"""
Simple data sync runner that avoids import issues
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def generate_mock_calendar_data():
    """Generate mock calendar data for demo"""
    events = []
    for i in range(5):
        events.append({
            "id": f"event_{i}",
            "summary": f"Meeting {i+1}",
            "start": {"dateTime": f"2024-03-0{i+1}T10:00:00"},
            "end": {"dateTime": f"2024-03-0{i+1}T11:00:00"},
            "location": "Conference Room",
            "description": f"Demo meeting {i+1}"
        })
    return events

def generate_mock_drive_data():
    """Generate mock drive data for demo"""
    documents = []
    for i in range(5):
        documents.append({
            "id": f"doc_{i}",
            "name": f"Document {i+1}.pdf",
            "modifiedTime": f"2024-03-0{i+1}T14:00:00",
            "createdTime": f"2024-03-0{i+1}T13:00:00",
            "owners": [{"displayName": "User"}],
            "lastModifyingUser": {"displayName": "User"},
            "mimeType": "application/pdf"
        })
    return documents

def generate_mock_location_data():
    """Generate mock location data for demo"""
    locations = []
    for i in range(10):
        locations.append({
            "timestamp": f"2024-03-0{i+1}T12:00:00Z",
            "latitude": -33.8688 + (i * 0.001),
            "longitude": 151.2093 + (i * 0.001),
            "activity": "walking" if i % 2 == 0 else "driving"
        })
    return locations

def generate_mock_fit_data():
    """Generate mock fitness data for demo"""
    activities = []
    for i in range(7):
        activities.append({
            "date": f"2024-03-0{i+1}",
            "steps": 8000 + (i * 500),
            "calories": 2000 + (i * 100),
            "active_minutes": 30 + (i * 5)
        })
    return activities

def main():
    """Main function to sync all data sources"""
    print("🚀 Starting Data Sync...")
    
    # Create output directory
    output_dir = Path("data_sync")
    output_dir.mkdir(exist_ok=True)
    
    # Generate mock data for all sources
    print("📊 Generating mock calendar data...")
    calendar_data = generate_mock_calendar_data()
    
    print("📁 Generating mock drive data...")
    drive_data = generate_mock_drive_data()
    
    print("📍 Generating mock location data...")
    location_data = generate_mock_location_data()
    
    print("🏃 Generating mock fitness data...")
    fit_data = generate_mock_fit_data()
    
    # Format data for RAG
    formatted_data = {}
    
    # Calendar events
    formatted_calendar = []
    for event in calendar_data:
        formatted_event = {
            "id": f"cal_{event['id']}",
            "text": f"{event['summary']} at {event['start']['dateTime']}",
            "metadata": {
                "type": "calendar_event",
                "start_time": event['start']['dateTime'],
                "end_time": event['end']['dateTime'],
                "location": event.get('location', ''),
                "description": event.get('description', ''),
                "synced_at": datetime.now().isoformat() + "Z",
            },
        }
        formatted_calendar.append(formatted_event)
    
    # Drive documents
    formatted_drive = []
    for doc in drive_data:
        formatted_doc = {
            "id": f"doc_{doc['id']}",
            "text": f"Document: {doc['name']} (last modified: {doc['modifiedTime']})",
            "metadata": {
                "type": "document",
                "name": doc["name"],
                "id": doc["id"],
                "modifiedTime": doc["modifiedTime"],
                "createdTime": doc.get("createdTime"),
                "mimeType": doc["mimeType"],
                "synced_at": datetime.now().isoformat() + "Z",
            },
        }
        formatted_drive.append(formatted_doc)
    
    # Location data
    formatted_location = []
    for loc in location_data:
        formatted_loc = {
            "id": f"loc_{loc['timestamp']}",
            "text": f"Location at {loc['timestamp']}: lat={loc['latitude']}, lon={loc['longitude']}, activity={loc['activity']}",
            "metadata": {
                "type": "location",
                "latitude": loc['latitude'],
                "longitude": loc['longitude'],
                "activity": loc['activity'],
                "timestamp": loc['timestamp'],
                "synced_at": datetime.now().isoformat() + "Z",
            },
        }
        formatted_location.append(formatted_loc)
    
    # Fitness data
    formatted_fit = []
    for activity in fit_data:
        formatted_act = {
            "id": f"fit_{activity['date']}",
            "text": f"Fitness on {activity['date']}: {activity['steps']} steps, {activity['calories']} calories, {activity['active_minutes']} active minutes",
            "metadata": {
                "type": "fitness",
                "date": activity['date'],
                "steps": activity['steps'],
                "calories": activity['calories'],
                "active_minutes": activity['active_minutes'],
                "synced_at": datetime.now().isoformat() + "Z",
            },
        }
        formatted_fit.append(formatted_act)
    
    # Save all data
    data_sources = {
        "calendar": formatted_calendar,
        "drive": formatted_drive,
        "location": formatted_location,
        "fit": formatted_fit,
    }
    
    # Save to files
    for source, data in data_sources.items():
        filename = output_dir / f"{source}_sync.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    
    # Save summary
    summary = {source: len(data) for source, data in data_sources.items()}
    summary_filename = output_dir / "sync_summary.json"
    with open(summary_filename, "w") as f:
        json.dump(summary, f, indent=2)
    
    total_items = sum(len(data) for data in data_sources.values())
    
    print(f"\n✅ Data sync completed successfully!")
    print(f"📊 Summary:")
    for source, count in summary.items():
        print(f"   - {source.capitalize()}: {count} items")
    print(f"   - Total: {total_items} items")
    print(f"📁 Files saved to: {output_dir}/")
    
    return True

if __name__ == "__main__":
    main()