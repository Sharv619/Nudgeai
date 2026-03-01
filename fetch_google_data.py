#!/usr/bin/env python3
"""
Fetch real data from Google APIs and sync it to the project
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Import from existing modules
from data_ingestion.calendar.fetch_calendar_events import (
    fetch_events,
    get_google_calendar_service,
)
from data_ingestion.drive.fetch_drive_documents import (
    fetch_documents as fetch_drive_documents,
    get_google_drive_service,
)

def fetch_real_calendar_data():
    """Fetch real calendar data from Google Calendar API."""
    try:
        print("Fetching calendar data from Google Calendar API...")
        
        # Get calendar service
        service = get_google_calendar_service()
        
        # Fetch events (last 30 days)
        events = fetch_events(service, max_results=50)
        
        # Format for RAG
        formatted_events = []
        for event in events:
            start_time = event["start"].get("dateTime", event["start"].get("date"))
            formatted_event = {
                "id": f"cal_{event.get('id', 'unknown')}",
                "text": f"{event.get('summary', 'No title')} at {start_time}",
                "metadata": {
                    "type": "calendar_event",
                    "start_time": start_time,
                    "end_time": event.get("end", {}).get(
                        "dateTime", event.get("end", {}).get("date")
                    ),
                    "attendees": [
                        a.get("email", "") for a in event.get("attendees", [])
                    ],
                    "location": event.get("location", ""),
                    "description": event.get("description", ""),
                    "synced_at": datetime.now().isoformat() + "Z",
                },
            }
            formatted_events.append(formatted_event)
        
        print(f"✅ Calendar data fetched: {len(formatted_events)} events")
        return formatted_events
        
    except Exception as e:
        print(f"❌ Calendar data fetch failed: {e}")
        return []

def fetch_real_drive_data():
    """Fetch real Drive data from Google Drive API."""
    try:
        print("Fetching documents from Google Drive API...")
        
        # Get drive service
        service = get_google_drive_service()
        
        # Fetch documents
        documents = fetch_drive_documents(service, max_results=50)
        
        # Format for RAG
        formatted_docs = []
        for doc in documents:
            formatted_doc = {
                "id": f"doc_{doc['id']}",
                "text": f"Document: {doc['name']} (last modified: {doc['modifiedTime']})",
                "metadata": {
                    "type": "document",
                    "name": doc["name"],
                    "id": doc["id"],
                    "modifiedTime": doc["modifiedTime"],
                    "createdTime": doc.get("createdTime"),
                    "owners": doc.get("owners", []),
                    "lastModifyingUser": doc.get("lastModifyingUser", {}),
                    "mimeType": doc["mimeType"],
                    "synced_at": datetime.now().isoformat() + "Z",
                },
            }
            formatted_docs.append(formatted_doc)
        
        print(f"✅ Drive data fetched: {len(formatted_docs)} documents")
        return formatted_docs
        
    except Exception as e:
        print(f"❌ Drive data fetch failed: {e}")
        return []

def save_google_data(calendar_data, drive_data):
    """Save the fetched Google data."""
    # Create output directory
    output_dir = Path("data_sync")
    output_dir.mkdir(exist_ok=True)
    
    # Save calendar data
    if calendar_data:
        calendar_file = output_dir / "calendar_sync.json"
        with open(calendar_file, "w") as f:
            json.dump(calendar_data, f, indent=2)
        print(f"📁 Calendar data saved to: {calendar_file}")
    
    # Save drive data
    if drive_data:
        drive_file = output_dir / "drive_sync.json"
        with open(drive_file, "w") as f:
            json.dump(drive_data, f, indent=2)
        print(f"📁 Drive data saved to: {drive_file}")
    
    # Update summary
    summary = {
        "calendar": len(calendar_data),
        "drive": len(drive_data),
        "location": 0,  # Mock data
        "fit": 0,       # Mock data
        "fetched_at": datetime.now().isoformat() + "Z",
        "source": "Google APIs"
    }
    
    summary_file = output_dir / "sync_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"📊 Summary updated: {summary}")

def main():
    """Main function to fetch real Google data."""
    print("🚀 Fetching Real Google Data...")
    
    # Fetch real data
    calendar_data = fetch_real_calendar_data()
    drive_data = fetch_real_drive_data()
    
    # Save data
    save_google_data(calendar_data, drive_data)
    
    total_items = len(calendar_data) + len(drive_data)
    print(f"\n🎉 Google data fetch completed!")
    print(f"📊 Total items: {total_items}")
    print(f"📁 Files saved to: data_sync/")
    
    return True

if __name__ == "__main__":
    main()