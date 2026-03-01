#!/usr/bin/env python3
"""
Parser for Google Semantic Location History JSON format.
Handles the new Google Location History format which includes semantic place names
and richer location context data.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SemanticLocationHistoryParser:
    """Parses Google Semantic Location History JSON files."""

    def __init__(self):
        self.entries = []

    def load_from_takeout_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load semantic location history from a Google Takeout JSON file.

        Args:
            file_path: Path to the Semantic Location History JSON file

        Returns:
            List of parsed location entries
        """
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract timeline objects
            timeline_objects = data.get("timelineObjects", [])
            parsed_entries = []

            for obj in timeline_objects:
                if "placeVisit" in obj:
                    entry = self._parse_place_visit(obj["placeVisit"])
                    if entry:
                        parsed_entries.append(entry)
                elif "activitySegment" in obj:
                    entry = self._parse_activity_segment(obj["activitySegment"])
                    if entry:
                        parsed_entries.append(entry)

            self.entries = parsed_entries
            logger.info(
                f"Parsed {len(parsed_entries)} location entries from {file_path}"
            )
            return parsed_entries

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing location history file {file_path}: {e}")
            return []

    def load_from_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Load semantic location history from multiple JSON files in a directory.

        Args:
            directory_path: Path to directory containing Semantic Location History files

        Returns:
            List of parsed location entries
        """
        all_entries = []
        directory = Path(directory_path)

        # Look for all JSON files in the directory
        json_files = list(directory.glob("*.json"))
        if not json_files:
            logger.warning(f"No JSON files found in {directory_path}")
            return []

        logger.info(f"Found {len(json_files)} JSON files to process")

        for json_file in json_files:
            logger.info(f"Processing {json_file.name}")
            entries = self.load_from_takeout_file(str(json_file))
            all_entries.extend(entries)

        # Sort by timestamp
        all_entries.sort(key=lambda x: x["timestamp"], reverse=True)
        logger.info(f"Loaded {len(all_entries)} total entries from directory")

        return all_entries

    def _parse_place_visit(
        self, place_visit: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Parse a place visit from semantic location history.

        Args:
            place_visit: Place visit dictionary from JSON

        Returns:
            Parsed location entry or None if invalid
        """
        try:
            # Extract location info
            location = place_visit.get("location", {})
            address = location.get("address", "Unknown")
            name = location.get("name", location.get("address", "Unknown"))
            latitude = location.get("latitudeE7", 0) / 1e7
            longitude = location.get("longitudeE7", 0) / 1e7
            place_id = location.get("placeId", "")
            location_confidence = location.get("confidence", 0)

            # Extract time info
            start_time = self._parse_timestamp(
                place_visit.get("duration", {}).get("startTimestamp", "")
            )
            end_time = self._parse_timestamp(
                place_visit.get("duration", {}).get("endTimestamp", "")
            )

            # Determine location type based on name/address patterns
            location_type = self._infer_location_type(
                name, address, latitude, longitude
            )

            # Extract other attributes
            center_lat = location.get("latitudeE7", 0) / 1e7
            center_lng = location.get("longitudeE7", 0) / 1e7
            place_likelihood = place_visit.get("placeConfidence", "LIKELY")

            entry = {
                "id": f"pv_{start_time.replace(':', '').replace('-', '').replace('.', '')}",
                "timestamp": start_time,
                "end_timestamp": end_time,
                "latitude": latitude,
                "longitude": longitude,
                "location_type": location_type,
                "place_name": name,
                "address": address,
                "place_id": place_id,
                "center_lat": center_lat,
                "center_lng": center_lng,
                "location_confidence": location_confidence,
                "place_likelihood": place_likelihood,
                "accuracy": location.get("accuracyInMeters", 0),
                "semantic_type": "placeVisit",
            }

            return entry

        except Exception as e:
            logger.error(f"Error parsing place visit: {e}")
            return None

    def _parse_activity_segment(
        self, activity_segment: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Parse an activity segment from semantic location history.

        Args:
            activity_segment: Activity segment dictionary from JSON

        Returns:
            Parsed location entry or None if invalid
        """
        try:
            # Extract time info
            start_time = self._parse_timestamp(
                activity_segment.get("duration", {}).get("startTimestamp", "")
            )
            end_time = self._parse_timestamp(
                activity_segment.get("duration", {}).get("endTimestamp", "")
            )

            # Extract start/end locations
            start_location = activity_segment.get("startLocation", {})
            end_location = activity_segment.get("endLocation", {})

            start_lat = start_location.get("latitudeE7", 0) / 1e7
            start_lng = start_location.get("longitudeE7", 0) / 1e7
            end_lat = end_location.get("latitudeE7", 0) / 1e7
            end_lng = end_location.get("longitudeE7", 0) / 1e7

            # Extract transportation mode
            activities = activity_segment.get("activityType", "UNKNOWN_ACTIVITY_TYPE")
            confidence = activity_segment.get("confidence", 0)

            # Create entry
            entry = {
                "id": f"as_{start_time.replace(':', '').replace('-', '').replace('.', '')}",
                "timestamp": start_time,
                "end_timestamp": end_time,
                "start_latitude": start_lat,
                "start_longitude": start_lng,
                "end_latitude": end_lat,
                "end_longitude": end_lng,
                "activity_type": activities,
                "confidence": confidence,
                "semantic_type": "activitySegment",
            }

            return entry

        except Exception as e:
            logger.error(f"Error parsing activity segment: {e}")
            return None

    def _parse_timestamp(self, timestamp_str: str) -> str:
        """
        Parse Google's timestamp format to ISO format.

        Args:
            timestamp_str: Google's timestamp format (e.g., '2023-01-15T10:30:45.123Z')

        Returns:
            ISO formatted timestamp
        """
        if not timestamp_str:
            return datetime.now().isoformat() + "Z"

        # Google timestamps are usually in ISO format already
        try:
            # Convert to datetime and back to ensure consistent format
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            return dt.isoformat() + "Z"
        except Exception:
            # Fallback to original if parsing fails
            return timestamp_str

    def _infer_location_type(
        self, name: str, address: str, lat: float, lng: float
    ) -> str:
        """
        Infer location type based on name, address, and coordinates.

        Args:
            name: Place name
            address: Place address
            lat: Latitude
            lng: Longitude

        Returns:
            Inferred location type
        """
        name_lower = name.lower()
        address_lower = address.lower()

        # Define patterns for different location types
        home_patterns = ["home", "house", "residence", "my place"]
        work_patterns = ["office", "work", "company", "corporate", "building"]
        gym_patterns = [
            "gym",
            "fitness",
            "sports",
            "exercise",
            "training",
            "health club",
        ]
        restaurant_patterns = [
            "restaurant",
            "cafe",
            "bar",
            "diner",
            "eat",
            "food",
            "meal",
        ]
        shopping_patterns = ["shop", "store", "mall", "market", "retail", "supermarket"]
        transit_patterns = ["station", "airport", "bus", "train", "transit", "terminal"]

        # Check patterns
        for pattern in home_patterns:
            if pattern in name_lower or pattern in address_lower:
                return "home"
        for pattern in work_patterns:
            if pattern in name_lower or pattern in address_lower:
                return "work"
        for pattern in gym_patterns:
            if pattern in name_lower or pattern in address_lower:
                return "exercise"
        for pattern in restaurant_patterns:
            if pattern in name_lower or pattern in address_lower:
                return "dining"
        for pattern in shopping_patterns:
            if pattern in name_lower or pattern in address_lower:
                return "shopping"
        for pattern in transit_patterns:
            if pattern in name_lower or pattern in address_lower:
                return "transit"

        # Default to other if no pattern matches
        return "other"

    def filter_by_location_type(self, location_type: str) -> List[Dict[str, Any]]:
        """
        Filter entries by location type.

        Args:
            location_type: Type of location to filter ('home', 'work', 'exercise', etc.)

        Returns:
            Filtered list of entries
        """
        return [
            entry
            for entry in self.entries
            if entry.get("location_type") == location_type
        ]

    def filter_by_time_range(
        self, start_time: str, end_time: str
    ) -> List[Dict[str, Any]]:
        """
        Filter entries by time range.

        Args:
            start_time: Start time in ISO format
            end_time: End time in ISO format

        Returns:
            Filtered list of entries
        """
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

        filtered_entries = []
        for entry in self.entries:
            entry_time = datetime.fromisoformat(
                entry["timestamp"].replace("Z", "+00:00")
            )
            if start_dt <= entry_time <= end_dt:
                filtered_entries.append(entry)

        return filtered_entries


def main():
    """Example usage of the SemanticLocationHistoryParser."""
    parser = SemanticLocationHistoryParser()

    # Example: Load from a single file
    # entries = parser.load_from_takeout_file("SemanticLocationHistory.json")

    # Example: Load from a directory containing multiple JSON files
    # entries = parser.load_from_directory("./location_data/")

    print(f"Successfully parsed location history")


if __name__ == "__main__":
    main()
