#!/usr/bin/env python3
"""
Unified data synchronization manager for all Google API data sources.
Coordinates calendar, drive, location, and fit data ingestion.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable
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
from data_ingestion.location.fetch_location_history import (
    generate_mock_location_data,
    format_locations_for_rag,
)
from data_ingestion.fit.fetch_fit_data import generate_mock_fit_data, format_fit_for_rag

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/data_sync.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class DataSyncManager:
    """Manages synchronization of data from all Google API sources."""

    def __init__(self):
        self.data_sources = {
            "calendar": self._sync_calendar,
            "drive": self._sync_drive,
            "location": self._sync_location,
            "fit": self._sync_fit,
        }
        self.ensure_logs_dir()

    def ensure_logs_dir(self):
        """Ensure logs directory exists."""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

    def _sync_calendar(self, params: Dict[str, Any]) -> List[Dict]:
        """Sync calendar events."""
        try:
            logger.info("Starting calendar sync...")
            max_results = params.get("max_results", 10)

            # Get calendar service
            try:
                service = get_google_calendar_service()
            except Exception as auth_error:
                logger.error(f"Calendar authentication failed: {auth_error}")
                # For demo purposes, return empty list instead of failing
                return []

            # Fetch events
            events = fetch_events(service, max_results)

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

            logger.info(f"Calendar sync completed: {len(formatted_events)} events")
            return formatted_events

        except Exception as e:
            logger.error(f"Calendar sync failed: {e}")
            return []

    def _sync_drive(self, params: Dict[str, Any]) -> List[Dict]:
        """Sync Google Drive documents."""
        try:
            logger.info("Starting drive sync...")
            max_results = params.get("max_results", 10)

            # Get drive service
            try:
                service = get_google_drive_service()
            except Exception as auth_error:
                logger.error(f"Drive authentication failed: {auth_error}")
                # For demo purposes, return empty list instead of failing
                return []

            # Fetch documents
            documents = fetch_drive_documents(service, max_results)

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

            logger.info(f"Drive sync completed: {len(formatted_docs)} documents")
            return formatted_docs

        except Exception as e:
            logger.error(f"Drive sync failed: {e}")
            return []

    def _sync_location(self, params: Dict[str, Any]) -> List[Dict]:
        """Sync location history from Google Takeout data."""
        try:
            logger.info("Starting location sync...")

            # Check if Google Takeout location data path is provided
            takeout_path = params.get("takeout_path")
            days = params.get("days", 14)  # Default to 14 days

            if takeout_path and os.path.exists(takeout_path):
                # Load from Google Takeout data
                from data_ingestion.location.fetch_location_history import (
                    load_google_location_data,
                )

                logger.info(f"Loading location data from: {takeout_path}")
                locations = load_google_location_data(takeout_path)

                # If days parameter is specified, filter by recent days
                if days and days > 0:
                    cutoff_date = (
                        datetime.now() - timedelta(days=days)
                    ).isoformat() + "Z"
                    locations = [
                        loc
                        for loc in locations
                        if loc.get("timestamp", "") >= cutoff_date
                    ]
            else:
                # Fallback to generating mock data
                logger.warning(
                    "No Google Takeout data found, generating mock data for demo"
                )
                from data_ingestion.location.fetch_location_history import (
                    generate_mock_location_data,
                )

                locations = generate_mock_location_data(days)

            # Format for RAG
            from data_ingestion.location.fetch_location_history import (
                format_locations_for_rag,
            )

            formatted_locations = format_locations_for_rag(locations)

            logger.info(
                f"Location sync completed: {len(formatted_locations)} locations"
            )
            return formatted_locations

        except Exception as e:
            logger.error(f"Location sync failed: {e}")
            return []

    def _sync_fit(self, params: Dict[str, Any]) -> List[Dict]:
        """Sync fitness data (mock data for demo)."""
        try:
            logger.info("Starting fit sync...")
            days = params.get("days", 7)

            # Generate mock fit data
            activities = generate_mock_fit_data(days)

            # Format for RAG
            formatted_activities = format_fit_for_rag(activities)

            logger.info(f"Fit sync completed: {len(formatted_activities)} activities")
            return formatted_activities

        except Exception as e:
            logger.error(f"Fit sync failed: {e}")
            return []

    def sync_all(self, params: Dict[str, Any] = {}) -> Dict[str, List[Dict]]:
        """Sync all data sources."""
        if params is None:
            params = {}

        results = {}
        for source, sync_func in self.data_sources.items():
            source_params = params.get(source, {})
            results[source] = sync_func(source_params)

        total_items = sum(len(items) for items in results.values())
        logger.info(
            f"All syncs completed: {total_items} total items from {len(results)} sources"
        )

        return results

    def sync_source(self, source: str, params: Dict[str, Any] = {}) -> List[Dict]:
        """Sync a specific data source."""
        if source not in self.data_sources:
            raise ValueError(f"Unknown data source: {source}")

        if params is None:
            params = {}

        return self.data_sources[source](params)

    def save_sync_results(
        self, results: Dict[str, List[Dict]], directory: str = "data_sync"
    ) -> str:
        """Save sync results to JSON files."""
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)

        summary = {}
        for source, data in results.items():
            filename = dir_path / f"{source}_sync.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            summary[source] = len(data)

        # Save summary
        summary_filename = dir_path / "sync_summary.json"
        with open(summary_filename, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Results saved to {directory}/ - Summary: {summary}")
        return str(dir_path)


def main():
    """Main function to demonstrate the sync manager."""
    print("Initializing Data Sync Manager...")

    manager = DataSyncManager()

    # Example sync parameters
    sync_params = {
        "calendar": {"max_results": 10},
        "drive": {"max_results": 10},
        "location": {"days": 7},
        "fit": {"days": 7},
    }

    # Perform sync
    results = manager.sync_all(sync_params)

    # Print summary
    total_items = 0
    for source, data in results.items():
        count = len(data)
        total_items += count
        print(f"{source.capitalize()}: {count} items")

    print(f"Total: {total_items} items synced")

    # Save results
    output_dir = manager.save_sync_results(results)
    print(f"Results saved to: {output_dir}")


if __name__ == "__main__":
    main()
