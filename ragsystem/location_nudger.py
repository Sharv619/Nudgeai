"""
Module for location-based nudging system that detects when user is near important locations
and provides contextual nudges based on calendar events and other factors.
"""

import math
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from ragsystem.mcp_integration import rag_mcp_integrator


logger = logging.getLogger(__name__)


class LocationNudger:
    """
    Provides location-based nudges when user is near important locations.
    """

    def __init__(self):
        self.rag_integrator = rag_mcp_integrator
        # Define important locations with coordinates and radius (in meters)
        self.important_locations = {
            "gym": {
                "coordinates": (37.7646, -122.4212),  # Default gym coordinates
                "radius": 100,  # 100 meters radius
                "nudge_message": "You're near the gym! Would you like to squeeze in a quick workout?",
                "conflict_keywords": ["delivery", "appointment", "meeting"],
            },
            "office": {
                "coordinates": (37.7814, -122.4095),  # Default office coordinates
                "radius": 100,
                "nudge_message": "You've reached the office. Ready for your day?",
                "conflict_keywords": ["work-from-home", "remote"],
            },
            "home": {
                "coordinates": (37.7749, -122.4194),  # Default home coordinates
                "radius": 100,
                "nudge_message": "Welcome home! How was your day?",
                "conflict_keywords": ["out-of-town", "travel"],
            },
        }

    def update_location_coordinates(self, location_type: str, lat: float, lng: float):
        """
        Update coordinates for a specific location type.
        """
        if location_type in self.important_locations:
            self.important_locations[location_type]["coordinates"] = (lat, lng)

    def haversine_distance(
        self, coord1: Tuple[float, float], coord2: Tuple[float, float]
    ) -> float:
        """
        Calculate the great circle distance between two points on the earth (specified in decimal degrees)
        Returns distance in meters.
        """
        lat1, lon1 = coord1
        lat2, lon2 = coord2

        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # Radius of earth in meters
        r = 6371000
        return c * r

    def is_near_location(
        self, user_lat: float, user_lng: float, location_type: str
    ) -> bool:
        """
        Check if user is within radius of a specific location type.
        """
        if location_type not in self.important_locations:
            return False

        location_coords = self.important_locations[location_type]["coordinates"]
        radius = self.important_locations[location_type]["radius"]

        distance = self.haversine_distance((user_lat, user_lng), location_coords)
        return distance <= radius

    def get_current_conflicts(self) -> List[Dict[str, Any]]:
        """
        Check for potential conflicts in calendar that might affect nudges.
        """
        # Look for upcoming events that might conflict with location-based suggestions
        current_time = datetime.now()
        time_window_start = current_time.isoformat()
        time_window_end = (current_time + timedelta(hours=2)).isoformat()

        # Search for calendar events that might conflict
        query = f"upcoming events between {time_window_start} and {time_window_end}"
        results = self.rag_integrator.semantic_search(
            query, k=5, filters={"type": "calendar_event"}
        )

        conflicts = []
        for result in results:
            metadata = result["document"]["metadata"]
            event_title = metadata.get("summary", metadata.get("title", ""))

            # Check for potential conflicts with location-based nudges
            for location_info in self.important_locations.values():
                for keyword in location_info["conflict_keywords"]:
                    if keyword.lower() in event_title.lower():
                        conflicts.append(
                            {
                                "event": event_title,
                                "time": metadata.get("start_time", "unknown"),
                                "conflict_with": location_info.get(
                                    "nudge_message", "location activity"
                                ),
                            }
                        )

        return conflicts

    def generate_location_nudge(
        self, user_lat: float, user_lng: float
    ) -> Optional[Dict[str, Any]]:
        """
        Generate appropriate nudge based on user location and potential conflicts.
        """
        # Check which important locations user is near
        nearby_locations = []
        for location_type, location_info in self.important_locations.items():
            if self.is_near_location(user_lat, user_lng, location_type):
                nearby_locations.append((location_type, location_info))

        if not nearby_locations:
            return None

        # Get any conflicts that might affect the nudge
        conflicts = self.get_current_conflicts()

        nudges = []
        for location_type, location_info in nearby_locations:
            nudge = {
                "location_type": location_type,
                "nudge_message": location_info["nudge_message"],
                "distance": self.haversine_distance(
                    (user_lat, user_lng), location_info["coordinates"]
                ),
                "coordinates": location_info["coordinates"],
                "conflicts": [],
                "should_nudge": True,
            }

            # Check for conflicts specific to this location
            location_conflicts = []
            for conflict in conflicts:
                if isinstance(conflict, dict) and "conflict_with" in conflict:
                    conflict_with = conflict.get("conflict_with", "")
                    if location_type.lower() in str(conflict_with).lower():
                        location_conflicts.append(conflict)
                        nudge["should_nudge"] = (
                            False  # Don't nudge if there's a conflict
                        )

            nudge["conflicts"] = location_conflicts
            nudges.append(nudge)

        # Return the most relevant nudge (closest location with highest priority)
        if nudges:
            # Prioritize gym nudges if there are no conflicts, otherwise return first nudge
            priority_order = ["gym", "office", "home"]
            nudges.sort(
                key=lambda x: (
                    priority_order.index(x["location_type"])
                    if x["location_type"] in priority_order
                    else 999
                )
            )
            return nudges[0]

        return None

    def update_important_locations_from_data(self):
        """
        Dynamically update important locations based on historical location data.
        """
        # Search for frequently visited locations in the RAG system
        query = "most frequently visited locations"
        results = self.rag_integrator.location_pattern_search(
            "home", {"start": "2024-01-01T00:00:00", "end": datetime.now().isoformat()}
        )

        # Update home location if we find a consistent pattern
        if results:
            # For simplicity, we'll take the most recent home location as reference
            for result in results:
                metadata = result["document"]["metadata"]
                if metadata.get("location_type") == "home":
                    lat = metadata.get("latitude")
                    lng = metadata.get("longitude")
                    if lat and lng:
                        self.update_location_coordinates("home", float(lat), float(lng))
                        break


# Global instance for use in the system
location_nudger = LocationNudger()
