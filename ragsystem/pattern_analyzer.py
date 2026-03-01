"""
Pattern Analyzer module for detecting behavioral patterns from calendar, location, and fitness data.
"""

import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple
import statistics

from ragsystem.mcp_integration import rag_mcp_integrator


class PatternAnalyzer:
    """
    Analyzes behavioral patterns from multiple data sources to identify trends and correlations.
    """

    def __init__(self):
        self.rag_integrator = rag_mcp_integrator

    def analyze_daily_patterns(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze daily patterns across all data sources.
        """
        # Get recent data from the RAG system
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        end_date = datetime.now().isoformat()

        # Search for calendar, location, and fitness data
        calendar_results = self.rag_integrator.semantic_search(
            f"calendar events in the last {days} days",
            k=100,
            filters={"type": "calendar_event"},
        )

        location_results = self.rag_integrator.semantic_search(
            f"location visits in the last {days} days",
            k=100,
            filters={"type": "location"},
        )

        fitness_results = self.rag_integrator.semantic_search(
            f"fitness activities in the last {days} days",
            k=100,
            filters={"type": "fitness_activity"},
        )

        # Extract and analyze patterns from each data type
        daily_patterns = {
            "calendar_analysis": self._analyze_calendar_patterns(calendar_results),
            "location_analysis": self._analyze_location_patterns(location_results),
            "fitness_analysis": self._analyze_fitness_patterns(fitness_results),
            "cross_correlations": self._find_cross_correlations(
                calendar_results, location_results, fitness_results
            ),
        }

        return daily_patterns

    def _analyze_calendar_patterns(
        self, calendar_results: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze patterns in calendar data.
        """
        if not calendar_results:
            return {
                "patterns": [],
                "summary": "No calendar data available for analysis",
            }

        # Extract time-based patterns
        hour_counts = Counter()
        day_of_week_counts = Counter()
        event_types = Counter()

        for result in calendar_results:
            metadata = result["document"]["metadata"]
            start_time_str = metadata.get("start_time", "")

            if start_time_str:
                try:
                    start_time = datetime.fromisoformat(
                        start_time_str.replace("Z", "+00:00")
                    )
                    hour_counts[start_time.hour] += 1
                    day_of_week_counts[start_time.weekday()] += 1  # 0=Monday, 6=Sunday

                    # Extract event type from summary
                    summary = metadata.get("summary", "").lower()
                    if "meeting" in summary or "call" in summary:
                        event_types["meetings"] += 1
                    elif "personal" in summary or "break" in summary:
                        event_types["personal"] += 1
                    elif "work" in summary:
                        event_types["work"] += 1
                    else:
                        event_types["other"] += 1
                except ValueError:
                    continue

        # Identify peak hours and days
        peak_hours = [hour for hour, count in hour_counts.most_common(3)]
        peak_days = [day for day, count in day_of_week_counts.most_common(2)]

        return {
            "peak_hours": peak_hours,
            "peak_days": peak_days,
            "event_distribution": dict(event_types),
            "total_events": sum(hour_counts.values()),
            "busiest_day": day_of_week_counts.most_common(1)[0][0]
            if day_of_week_counts
            else None,
        }

    def _analyze_location_patterns(
        self, location_results: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze patterns in location data.
        """
        if not location_results:
            return {
                "patterns": [],
                "summary": "No location data available for analysis",
            }

        location_types = Counter()
        visit_times = []
        locations_by_type = defaultdict(list)

        for result in location_results:
            metadata = result["document"]["metadata"]
            location_type = metadata.get("location_type", "unknown")
            location_types[location_type] += 1

            # Track time patterns
            timestamp = metadata.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    visit_times.append(dt.hour)
                    locations_by_type[location_type].append(dt)
                except ValueError:
                    continue

        # Analyze location visit patterns
        most_visited = location_types.most_common(3)
        peak_visit_hours = Counter(visit_times).most_common(3)

        return {
            "most_visited_locations": most_visited,
            "peak_visit_hours": [hour for hour, count in peak_visit_hours],
            "location_type_distribution": dict(location_types),
            "total_visits": sum(location_types.values()),
            "location_routines": {
                loc_type: len(times) for loc_type, times in locations_by_type.items()
            },
        }

    def _analyze_fitness_patterns(self, fitness_results: List[Dict]) -> Dict[str, Any]:
        """
        Analyze patterns in fitness data.
        """
        if not fitness_results:
            return {"patterns": [], "summary": "No fitness data available for analysis"}

        activity_types = Counter()
        durations = []
        calories_burned = []
        activity_times = []

        for result in fitness_results:
            metadata = result["document"]["metadata"]
            activity_type = metadata.get("activity_type", "unknown")
            activity_types[activity_type] += 1

            # Collect metrics
            duration = metadata.get("duration_minutes")
            if duration:
                durations.append(duration)

            calories = metadata.get("calories")
            if calories:
                calories_burned.append(calories)

            timestamp = metadata.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    activity_times.append(dt.hour)
                except ValueError:
                    continue

        # Calculate statistics
        avg_duration = statistics.mean(durations) if durations else 0
        avg_calories = statistics.mean(calories_burned) if calories_burned else 0
        consistency_rate = len(fitness_results) / 7.0  # Assuming weekly analysis

        return {
            "activity_distribution": dict(activity_types),
            "avg_duration_minutes": avg_duration,
            "avg_calories_burned": avg_calories,
            "consistency_rate_per_week": consistency_rate,
            "peak_activity_hours": Counter(activity_times).most_common(3),
            "total_activities": len(fitness_results),
        }

    def _find_cross_correlations(
        self,
        calendar_results: List[Dict],
        location_results: List[Dict],
        fitness_results: List[Dict],
    ) -> Dict[str, Any]:
        """
        Find correlations between different data sources.
        """
        correlations = []

        # Convert results to time-indexed data for correlation analysis
        calendar_by_hour = defaultdict(list)
        location_by_hour = defaultdict(list)
        fitness_by_hour = defaultdict(list)

        # Index calendar events by hour
        for result in calendar_results:
            metadata = result["document"]["metadata"]
            start_time_str = metadata.get("start_time", "")
            if start_time_str:
                try:
                    start_time = datetime.fromisoformat(
                        start_time_str.replace("Z", "+00:00")
                    )
                    calendar_by_hour[start_time.hour].append(
                        metadata.get("summary", "")
                    )
                except ValueError:
                    continue

        # Index location visits by hour
        for result in location_results:
            metadata = result["document"]["metadata"]
            timestamp = metadata.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    location_by_hour[dt.hour].append(
                        metadata.get("location_type", "unknown")
                    )
                except ValueError:
                    continue

        # Index fitness activities by hour
        for result in fitness_results:
            metadata = result["document"]["metadata"]
            timestamp = metadata.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    fitness_by_hour[dt.hour].append(
                        metadata.get("activity_type", "unknown")
                    )
                except ValueError:
                    continue

        # Find hourly correlations
        common_hours = (
            set(calendar_by_hour.keys())
            & set(location_by_hour.keys())
            & set(fitness_by_hour.keys())
        )

        for hour in common_hours:
            cal_events = len(calendar_by_hour[hour])
            loc_visits = len(location_by_hour[hour])
            fit_activities = len(fitness_by_hour[hour])

            if cal_events > 0 and loc_visits > 0:
                correlations.append(
                    {
                        "hour": hour,
                        "calendar_events": cal_events,
                        "location_visits": loc_visits,
                        "fitness_activities": fit_activities,
                        "pattern_type": "busy_hour",
                    }
                )

        # Analyze day-level correlations
        calendar_by_day = defaultdict(list)
        location_by_day = defaultdict(list)
        fitness_by_day = defaultdict(list)

        # Index by day
        for result in calendar_results:
            metadata = result["document"]["metadata"]
            start_time_str = metadata.get("start_time", "")
            if start_time_str:
                try:
                    start_time = datetime.fromisoformat(
                        start_time_str.replace("Z", "+00:00")
                    )
                    day_key = start_time.date()
                    calendar_by_day[day_key].append(metadata.get("summary", ""))
                except ValueError:
                    continue

        for result in location_results:
            metadata = result["document"]["metadata"]
            timestamp = metadata.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    day_key = dt.date()
                    location_by_day[day_key].append(
                        metadata.get("location_type", "unknown")
                    )
                except ValueError:
                    continue

        for result in fitness_results:
            metadata = result["document"]["metadata"]
            timestamp = metadata.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    day_key = dt.date()
                    fitness_by_day[day_key].append(
                        metadata.get("activity_type", "unknown")
                    )
                except ValueError:
                    continue

        # Find day-level correlations
        common_days = (
            set(calendar_by_day.keys())
            & set(location_by_day.keys())
            & set(fitness_by_day.keys())
        )

        day_correlations = []
        for day in common_days:
            cal_count = len(calendar_by_day[day])
            loc_count = len(location_by_day[day])
            fit_count = len(fitness_by_day[day])

            # Calculate correlation score
            correlation_score = (cal_count * loc_count * fit_count) / max(
                cal_count + loc_count + fit_count, 1
            )

            day_correlations.append(
                {
                    "date": day.isoformat(),
                    "calendar_events": cal_count,
                    "location_visits": loc_count,
                    "fitness_activities": fit_count,
                    "correlation_score": correlation_score,
                }
            )

        return {
            "hourly_correlations": correlations,
            "daily_correlations": sorted(
                day_correlations, key=lambda x: x["correlation_score"], reverse=True
            )[:5],
            "total_correlated_days": len(common_days),
        }

    def generate_daily_summary(self, date: str = None) -> Dict[str, Any]:
        """
        Generate a daily summary for a specific date or the current day.
        """
        if date is None:
            target_date = datetime.now().date()
        else:
            target_date = datetime.fromisoformat(date).date()

        # Search for data on the specific date
        start_datetime = datetime.combine(target_date, datetime.min.time()).isoformat()
        end_datetime = datetime.combine(target_date, datetime.max.time()).isoformat()

        calendar_results = self.rag_integrator.semantic_search(
            f"calendar events on {target_date.isoformat()}",
            k=20,
            filters={"type": "calendar_event"},
        )

        location_results = self.rag_integrator.semantic_search(
            f"location visits on {target_date.isoformat()}",
            k=20,
            filters={"type": "location"},
        )

        fitness_results = self.rag_integrator.semantic_search(
            f"fitness activities on {target_date.isoformat()}",
            k=20,
            filters={"type": "fitness_activity"},
        )

        # Build daily summary
        daily_summary = {
            "date": target_date.isoformat(),
            "calendar_summary": self._build_calendar_summary(calendar_results),
            "location_summary": self._build_location_summary(location_results),
            "fitness_summary": self._build_fitness_summary(fitness_results),
            "day_rating": self._calculate_day_rating(
                calendar_results, location_results, fitness_results
            ),
            "recommendations": self._generate_recommendations(
                calendar_results, location_results, fitness_results
            ),
        }

        return daily_summary

    def _build_calendar_summary(self, calendar_results: List[Dict]) -> Dict[str, Any]:
        """
        Build a summary of calendar events for the day.
        """
        events = []
        total_hours_booked = 0

        for result in calendar_results:
            metadata = result["document"]["metadata"]
            start_time_str = metadata.get("start_time", "")
            end_time_str = metadata.get("end_time", "")

            events.append(
                {
                    "title": metadata.get("summary", "Untitled event"),
                    "start_time": start_time_str.split("T")[1][:5]
                    if "T" in start_time_str
                    else start_time_str,
                    "duration": self._calculate_duration(start_time_str, end_time_str),
                }
            )

            # Calculate total booked time
            if start_time_str and end_time_str:
                try:
                    start = datetime.fromisoformat(
                        start_time_str.replace("Z", "+00:00")
                    )
                    end = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
                    duration = (end - start).seconds / 3600.0  # in hours
                    total_hours_booked += duration
                except ValueError:
                    continue

        return {
            "total_events": len(events),
            "events": events,
            "total_booked_hours": round(total_hours_booked, 2),
            "busyness_level": "High"
            if total_hours_booked > 6
            else "Medium"
            if total_hours_booked > 3
            else "Low",
        }

    def _build_location_summary(self, location_results: List[Dict]) -> Dict[str, Any]:
        """
        Build a summary of location visits for the day.
        """
        locations = []
        location_types = Counter()

        for result in location_results:
            metadata = result["document"]["metadata"]
            locations.append(
                {
                    "name": metadata.get("place_name", "Unknown location"),
                    "type": metadata.get("location_type", "unknown"),
                    "arrival_time": metadata.get("timestamp", "")[:19].split("T")[1]
                    if "T" in metadata.get("timestamp", "")
                    else "",
                }
            )
            location_types[metadata.get("location_type", "unknown")] += 1

        return {
            "total_locations_visited": len(locations),
            "location_types_visited": dict(location_types),
            "locations": locations,
        }

    def _build_fitness_summary(self, fitness_results: List[Dict]) -> Dict[str, Any]:
        """
        Build a summary of fitness activities for the day.
        """
        activities = []
        total_calories = 0
        total_duration = 0

        for result in fitness_results:
            metadata = result["document"]["metadata"]
            activities.append(
                {
                    "type": metadata.get("activity_type", "unknown"),
                    "duration": metadata.get("duration_minutes", 0),
                    "calories_burned": metadata.get("calories", 0),
                    "time": metadata.get("timestamp", "")[:19].split("T")[1]
                    if "T" in metadata.get("timestamp", "")
                    else "",
                }
            )

            total_calories += metadata.get("calories", 0) or 0
            total_duration += metadata.get("duration_minutes", 0) or 0

        return {
            "total_activities": len(activities),
            "activities": activities,
            "total_calories_burned": total_calories,
            "total_duration_minutes": total_duration,
            "fitness_score": min(10, (total_calories / 100))
            if total_calories > 0
            else 0,
        }

    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """
        Calculate duration between two time strings.
        """
        if not start_time or not end_time:
            return "Unknown"

        try:
            start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            duration = end - start
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        except ValueError:
            return "Unknown"

    def _calculate_day_rating(
        self,
        calendar_results: List[Dict],
        location_results: List[Dict],
        fitness_results: List[Dict],
    ) -> int:
        """
        Calculate a rating for the day based on various factors.
        """
        # Base rating factors
        calendar_factor = min(
            10, len(calendar_results) * 0.5
        )  # More events = busier day
        location_factor = min(
            5, len(location_results) * 0.5
        )  # More locations = more active
        fitness_factor = min(
            5, len(fitness_results) * 2
        )  # Fitness activities = healthy day

        # Calculate overall rating (scale 1-10)
        rating = min(10, calendar_factor + location_factor + fitness_factor)
        return max(1, round(rating))

    def _generate_recommendations(
        self,
        calendar_results: List[Dict],
        location_results: List[Dict],
        fitness_results: List[Dict],
    ) -> List[str]:
        """
        Generate personalized recommendations based on the day's data.
        """
        recommendations = []

        # Analyze fitness data
        fitness_calories = sum(
            result["document"]["metadata"].get("calories", 0) or 0
            for result in fitness_results
        )

        if fitness_calories < 200:
            recommendations.append(
                "Consider adding a short workout to boost your energy."
            )

        # Analyze location data
        home_visits = sum(
            1
            for result in location_results
            if result["document"]["metadata"].get("location_type") == "home"
        )

        if home_visits > 1:  # Multiple home visits might indicate inefficiency
            recommendations.append(
                "Try to minimize trips home to save time and energy."
            )

        # Analyze calendar data
        calendar_time = 0
        for result in calendar_results:
            metadata = result["document"]["metadata"]
            start_time_str = metadata.get("start_time", "")
            end_time_str = metadata.get("end_time", "")

            if start_time_str and end_time_str:
                try:
                    start = datetime.fromisoformat(
                        start_time_str.replace("Z", "+00:00")
                    )
                    end = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
                    duration = (end - start).seconds / 3600.0  # in hours
                    calendar_time += duration
                except ValueError:
                    continue

        if calendar_time > 10:  # Over-scheduled
            recommendations.append(
                "Your schedule was quite packed today. Consider adding buffer time between meetings."
            )
        elif calendar_time < 4:  # Under-scheduled
            recommendations.append(
                "Your day was relatively light. Consider scheduling some personal development time."
            )

        return recommendations if recommendations else ["Great balance today!"]


# Global instance for use in the application
pattern_analyzer = PatternAnalyzer()
