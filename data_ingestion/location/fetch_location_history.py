#!/usr/bin/env python3
"""
Module to fetch and process Google Location History from Takeout.
Handles both Semantic Location History and older location history formats.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from data_ingestion.location.semantic_location_parser import (
    SemanticLocationHistoryParser,
)


def load_google_location_data(takeout_path: str) -> List[Dict]:
    """
    Load location data from Google Takeout export.

    Args:
        takeout_path: Path to the Google Takeout location history folder or file

    Returns:
        List of location history entries
    """
    if not os.path.exists(takeout_path):
        raise FileNotFoundError(f"Google Takeout path does not exist: {takeout_path}")

    parser = SemanticLocationHistoryParser()

    # Check if it's a directory containing multiple JSON files
    if os.path.isdir(takeout_path):
        locations = parser.load_from_directory(takeout_path)
    else:
        # Single file
        locations = parser.load_from_takeout_file(takeout_path)

    return locations


def generate_mock_location_data(days: int = 7) -> List[Dict]:
    """
    Generate realistic location patterns for demo purposes.
    This is kept as a fallback when Google Takeout data is not available.
    """
    import random

    locations = []
    home_lat, home_lng = 37.7749, -122.4194  # San Francisco as example
    office_lat, office_lng = 37.7814, -122.4095  # Nearby office
    gym_lat, gym_lng = 37.7646, -122.4212  # Local gym

    # Generate location patterns for the specified number of days
    for day_offset in range(days):
        base_date = datetime.now() - timedelta(days=day_offset)

        # Home in the morning (high probability)
        if random.random() < 0.9:  # 90% chance of being home in morning
            home_time = datetime.combine(
                base_date.date(), datetime.min.time()
            ) + timedelta(hours=8, minutes=random.randint(0, 30))
            locations.append(
                {
                    "id": f"loc_home_{home_time.strftime('%Y%m%d_%H%M%S')}",
                    "timestamp": home_time.isoformat() + "Z",
                    "latitude": home_lat + random.uniform(-0.001, 0.001),
                    "longitude": home_lng + random.uniform(-0.001, 0.001),
                    "location_type": "home",
                    "place_name": "Home",
                    "accuracy": random.randint(5, 15),
                }
            )

        # Office during work hours (high probability on weekdays)
        is_weekday = base_date.weekday() < 5  # Mon-Fri
        if is_weekday and random.random() < 0.8:  # 80% chance on weekdays
            office_time = datetime.combine(
                base_date.date(), datetime.min.time()
            ) + timedelta(hours=9, minutes=random.randint(0, 30))
            locations.append(
                {
                    "id": f"loc_office_{office_time.strftime('%Y%m%d_%H%M%S')}",
                    "timestamp": office_time.isoformat() + "Z",
                    "latitude": office_lat + random.uniform(-0.001, 0.001),
                    "longitude": office_lng + random.uniform(-0.001, 0.001),
                    "location_type": "work",
                    "place_name": "Office",
                    "accuracy": random.randint(5, 20),
                }
            )

        # Gym (moderate probability, more on certain days)
        gym_days = [0, 2, 4]  # Mon, Wed, Fri as example gym days
        if (
            base_date.weekday() in gym_days and random.random() < 0.6
        ):  # 60% chance on gym days
            gym_time = datetime.combine(
                base_date.date(), datetime.min.time()
            ) + timedelta(hours=18, minutes=random.randint(0, 45))
            locations.append(
                {
                    "id": f"loc_gym_{gym_time.strftime('%Y%m%d_%H%M%S')}",
                    "timestamp": gym_time.isoformat() + "Z",
                    "latitude": gym_lat + random.uniform(-0.001, 0.001),
                    "longitude": gym_lng + random.uniform(-0.001, 0.001),
                    "location_type": "exercise",
                    "place_name": "Gym",
                    "accuracy": random.randint(10, 25),
                }
            )

        # Evening at home (high probability)
        if random.random() < 0.95:  # 95% chance of being home in evening
            evening_time = datetime.combine(
                base_date.date(), datetime.min.time()
            ) + timedelta(hours=18, minutes=random.randint(0, 59))
            locations.append(
                {
                    "id": f"loc_home_evening_{evening_time.strftime('%Y%m%d_%H%M%S')}",
                    "timestamp": evening_time.isoformat() + "Z",
                    "latitude": home_lat + random.uniform(-0.001, 0.001),
                    "longitude": home_lng + random.uniform(-0.001, 0.001),
                    "location_type": "home",
                    "place_name": "Home",
                    "accuracy": random.randint(5, 15),
                }
            )

    return locations


def format_locations_for_rag(locations: List[Dict]) -> List[Dict]:
    """
    Format location data for RAG system with consistent structure.
    """
    formatted_locations = []
    for loc in locations:
        # Create text description for RAG
        if loc.get("semantic_type") == "activitySegment":
            text_desc = f"Traveled from ({loc.get('start_latitude', 0):.4f}, {loc.get('start_longitude', 0):.4f}) to ({loc.get('end_latitude', 0):.4f}, {loc.get('end_longitude', 0):.4f}) via {loc.get('activity_type', 'transportation')} on {loc['timestamp'][:10]}"
        else:
            text_desc = f"{loc['location_type']} visit at {loc.get('place_name', 'Unknown Location')} on {loc['timestamp'][:10]}"

        formatted_loc = {
            "id": loc["id"],
            "text": text_desc,
            "metadata": {
                "type": "location",
                "place_name": loc.get("place_name", "Unknown"),
                "location_type": loc.get("location_type", "other"),
                "timestamp": loc["timestamp"],
                "latitude": loc.get("latitude"),
                "longitude": loc.get("longitude"),
                "accuracy": loc.get("accuracy", 0),
                "address": loc.get("address", ""),
                "place_id": loc.get("place_id", ""),
                "location_confidence": loc.get("location_confidence", 0),
                "semantic_type": loc.get("semantic_type", "placeVisit"),
                "end_timestamp": loc.get("end_timestamp"),
            },
        }
        # Add specific fields for activity segments
        if loc.get("semantic_type") == "activitySegment":
            formatted_loc["metadata"]["activity_type"] = loc.get("activity_type")
            formatted_loc["metadata"]["start_latitude"] = loc.get("start_latitude")
            formatted_loc["metadata"]["start_longitude"] = loc.get("start_longitude")
            formatted_loc["metadata"]["end_latitude"] = loc.get("end_latitude")
            formatted_loc["metadata"]["end_longitude"] = loc.get("end_longitude")

        formatted_locations.append(formatted_loc)

    return formatted_locations


def main():
    """
    Main function to demonstrate location data processing.
    """
    print("Loading Google Location History data...")

    # Try to load from a common Google Takeout location
    takeout_paths = [
        "./Takeout/Location History/Semantic Location History/",  # Common location
        "./location_history.json",  # Single file
        "./Semantic Location History/",  # Alternative path
        "./google_location_data/",  # User-provided directory
    ]

    locations = None
    for path in takeout_paths:
        if os.path.exists(path):
            print(f"Found location data at: {path}")
            try:
                locations = load_google_location_data(path)
                break
            except Exception as e:
                print(f"Failed to load from {path}: {e}")
                continue

    # Fallback to mock data if no real data found
    if locations is None or len(locations) == 0:
        print("No real location data found, generating mock data for demo...")
        locations = generate_mock_location_data(days=14)

    print(f"Processed {len(locations)} location records")

    # Format for RAG system
    rag_formatted = format_locations_for_rag(locations)

    # Save to file
    output_file = "location_history_rag.json"
    with open(output_file, "w") as f:
        json.dump(rag_formatted, f, indent=2)
    print(f"Saved {len(rag_formatted)} location records to {output_file}")


if __name__ == "__main__":
    main()
