"""
Daily Summarizer module for generating comprehensive daily summaries and insights.
"""

import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple
import statistics

from ragsystem.pattern_analyzer import pattern_analyzer
from ragsystem.mcp_integration import rag_mcp_integrator


class DailySummarizer:
    """
    Generates comprehensive daily summaries with insights and analytics.
    """

    def __init__(self):
        self.pattern_analyzer = pattern_analyzer
        self.rag_integrator = rag_mcp_integrator

    def generate_weekly_summary(self, start_date: str = None) -> Dict[str, Any]:
        """
        Generate a comprehensive weekly summary with trends and insights.
        """
        if start_date is None:
            # Start from the beginning of the current week (Monday)
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())
        else:
            start_of_week = datetime.fromisoformat(start_date)

        # Generate daily summaries for the week
        weekly_data = {}
        for i in range(7):
            day = start_of_week + timedelta(days=i)
            day_summary = self.pattern_analyzer.generate_daily_summary(
                day.date().isoformat()
            )
            weekly_data[day.date().isoformat()] = day_summary

        # Aggregate weekly insights
        weekly_insights = self._aggregate_weekly_insights(weekly_data)

        return {
            "week_starting": start_of_week.date().isoformat(),
            "daily_summaries": weekly_data,
            "weekly_insights": weekly_insights,
            "trends": self._identify_weekly_trends(weekly_data),
            "recommendations": self._generate_weekly_recommendations(weekly_data),
        }

    def _aggregate_weekly_insights(
        self, weekly_data: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        Aggregate insights across the week.
        """
        # Count total events, locations visited, and fitness activities
        total_calendar_events = 0
        total_location_visits = 0
        total_fitness_activities = 0
        ratings = []

        for date, summary in weekly_data.items():
            total_calendar_events += summary["calendar_summary"]["total_events"]
            total_location_visits += summary["location_summary"][
                "total_locations_visited"
            ]
            total_fitness_activities += summary["fitness_summary"]["total_activities"]
            ratings.append(summary["day_rating"])

        avg_rating = statistics.mean(ratings) if ratings else 0
        busiest_day = (
            max(
                weekly_data.items(),
                key=lambda x: x[1]["calendar_summary"]["total_events"],
            )[0]
            if weekly_data
            else None
        )

        return {
            "total_calendar_events": total_calendar_events,
            "total_location_visits": total_location_visits,
            "total_fitness_activities": total_fitness_activities,
            "average_day_rating": round(avg_rating, 2),
            "busiest_day": busiest_day,
            "most_active_day": max(
                weekly_data.items(),
                key=lambda x: x[1]["fitness_summary"]["total_activities"],
            )[0]
            if weekly_data
            else None,
        }

    def _identify_weekly_trends(self, weekly_data: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Identify trends across the week.
        """
        # Track patterns
        location_types_over_week = Counter()
        activity_types_over_week = Counter()
        daily_busy_levels = []

        for date, summary in weekly_data.items():
            # Count location types
            for loc_type, count in summary["location_summary"][
                "location_types_visited"
            ].items():
                location_types_over_week[loc_type] += count

            # Count activity types
            for activity_type, count in summary["fitness_summary"]["activities"]:
                activity_types_over_week[activity_type] += count

            # Track busy levels
            daily_busy_levels.append(summary["calendar_summary"]["busyness_level"])

        # Identify most common location types and activities
        top_locations = location_types_over_week.most_common(3)
        top_activities = activity_types_over_week.most_common(3)

        # Identify pattern in busy levels
        busy_pattern = Counter(daily_busy_levels)

        return {
            "top_locations": top_locations,
            "top_activities": top_activities,
            "busy_level_pattern": dict(busy_pattern),
            "consistency_score": self._calculate_weekly_consistency(weekly_data),
        }

    def _calculate_weekly_consistency(self, weekly_data: Dict[str, Dict]) -> float:
        """
        Calculate a consistency score based on daily patterns.
        """
        if not weekly_data:
            return 0.0

        # Calculate consistency based on regular patterns
        days_with_fitness = sum(
            1
            for date, summary in weekly_data.items()
            if summary["fitness_summary"]["total_activities"] > 0
        )
        fitness_consistency = days_with_fitness / len(weekly_data)

        days_with_regular_schedule = sum(
            1
            for date, summary in weekly_data.items()
            if summary["calendar_summary"]["total_booked_hours"] > 2
        )
        schedule_consistency = days_with_regular_schedule / len(weekly_data)

        # Combine consistency scores
        overall_consistency = (fitness_consistency + schedule_consistency) / 2
        return round(overall_consistency * 10, 2)  # Scale to 0-10 range

    def _generate_weekly_recommendations(
        self, weekly_data: Dict[str, Dict]
    ) -> List[str]:
        """
        Generate recommendations based on the week's patterns.
        """
        recommendations = []

        # Analyze fitness patterns
        total_fitness_days = sum(
            1
            for date, summary in weekly_data.items()
            if summary["fitness_summary"]["total_activities"] > 0
        )

        if total_fitness_days < 3:
            recommendations.append(
                "Try to incorporate fitness activities on at least 3 days per week for better health."
            )

        # Analyze location patterns
        all_location_types = []
        for date, summary in weekly_data.items():
            all_location_types.extend(
                summary["location_summary"]["location_types_visited"].keys()
            )

        location_diversity = len(set(all_location_types))
        if location_diversity < 3:
            recommendations.append(
                "Consider visiting more diverse locations to break routine and stimulate creativity."
            )

        # Analyze schedule patterns
        avg_booked_hours = (
            statistics.mean(
                [
                    summary["calendar_summary"]["total_booked_hours"]
                    for date, summary in weekly_data.items()
                ]
            )
            if weekly_data
            else 0
        )

        if avg_booked_hours > 8:
            recommendations.append(
                "Your schedule seems very packed. Consider adding buffer time for rest and recovery."
            )
        elif avg_booked_hours < 4:
            recommendations.append(
                "Your schedule seems light. Consider adding more productive activities or learning time."
            )

        return recommendations if recommendations else ["Great week with good balance!"]

    def generate_behavioral_insights(self, days: int = 14) -> Dict[str, Any]:
        """
        Generate deep behavioral insights from the past N days of data.
        """
        # Use pattern analyzer to get detailed patterns
        patterns = self.pattern_analyzer.analyze_daily_patterns(days)

        # Generate behavioral insights
        insights = {
            "routine_identification": self._identify_routines(patterns),
            "habit_formation": self._analyze_habit_formation(patterns),
            "productivity_patterns": self._analyze_productivity_patterns(patterns),
            "lifestyle_assessment": self._assess_lifestyle(patterns),
            "personalized_recommendations": self._generate_behavioral_recommendations(
                patterns
            ),
        }

        return insights

    def _identify_routines(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify established routines from the patterns.
        """
        calendar_analysis = patterns["calendar_analysis"]
        location_analysis = patterns["location_analysis"]
        fitness_analysis = patterns["fitness_analysis"]

        routines = {
            "weekly_meetings_routine": calendar_analysis.get("busiest_day") is not None,
            "regular_locations": [
                item[0]
                for item in location_analysis.get("most_visited_locations", [])[:3]
            ],
            "fitness_routine": fitness_analysis.get("consistency_rate_per_week", 0)
            > 2.0,
            "peak_productivity_hours": calendar_analysis.get("peak_hours", [])[:3],
            "common_commute_routes": self._identify_commute_patterns(location_analysis),
        }

        return routines

    def _identify_commute_patterns(
        self, location_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Identify common commute routes based on location patterns.
        """
        # Look for patterns where user goes between home, office, gym regularly
        location_types = location_analysis.get("location_type_distribution", {})

        common_routes = []
        if location_types.get("home", 0) > 5 and location_types.get("work", 0) > 3:
            common_routes.append("Home to Office commute")

        if location_types.get("home", 0) > 5 and location_types.get("gym", 0) > 2:
            common_routes.append("Home to Gym route")

        return common_routes

    def _analyze_habit_formation(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze habit formation based on consistency patterns.
        """
        calendar_analysis = patterns["calendar_analysis"]
        location_analysis = patterns["location_analysis"]
        fitness_analysis = patterns["fitness_analysis"]

        # Calculate consistency scores
        calendar_consistency = (
            len(calendar_analysis.get("peak_days", [])) / 7.0
            if calendar_analysis.get("peak_days")
            else 0
        )
        fitness_consistency = fitness_analysis.get("consistency_rate_per_week", 0) / 7.0
        location_consistency = (
            len(location_analysis.get("location_routines", {})) / 7.0
            if location_analysis.get("location_routines")
            else 0
        )

        return {
            "calendar_habits_strength": calendar_consistency,
            "fitness_habits_strength": fitness_consistency,
            "location_habits_strength": location_consistency,
            "overall_habit_strength": (
                calendar_consistency + fitness_consistency + location_consistency
            )
            / 3.0,
            "habit_categories": {"strong": [], "developing": [], "weak": []},
        }

    def _analyze_productivity_patterns(
        self, patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze productivity patterns from the data.
        """
        calendar_analysis = patterns["calendar_analysis"]
        location_analysis = patterns["location_analysis"]
        fitness_analysis = patterns["fitness_analysis"]
        correlations = patterns["cross_correlations"]

        # Productivity indicators
        peak_hours = calendar_analysis.get("peak_hours", [])[:3]
        busy_days = calendar_analysis.get("peak_days", [])[:2]

        # Cross-correlation insights
        highly_correlated_days = len(correlations.get("daily_correlations", []))

        productivity_indicators = {
            "peak_productivity_hours": peak_hours,
            "most_productive_days": busy_days,
            "activity_balance_score": fitness_analysis.get(
                "consistency_rate_per_week", 0
            )
            * 10,
            "schedule_efficiency": len(calendar_analysis.get("event_distribution", {}))
            / 7.0
            if calendar_analysis.get("event_distribution")
            else 0,
            "cross_domain_integration": highly_correlated_days,
        }

        return productivity_indicators

    def _assess_lifestyle(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess overall lifestyle based on patterns.
        """
        calendar_analysis = patterns["calendar_analysis"]
        location_analysis = patterns["location_analysis"]
        fitness_analysis = patterns["fitness_analysis"]

        # Calculate lifestyle scores
        work_life_balance = self._calculate_work_life_balance(calendar_analysis)
        activity_level = self._calculate_activity_level(
            fitness_analysis, location_analysis
        )
        social_engagement = self._calculate_social_engagement(calendar_analysis)

        lifestyle_assessment = {
            "work_life_balance_score": work_life_balance,
            "physical_activity_score": activity_level,
            "social_engagement_score": social_engagement,
            "overall_health_indicator": (
                work_life_balance + activity_level + social_engagement
            )
            / 3.0,
            "lifestyle_category": self._categorize_lifestyle(
                work_life_balance, activity_level, social_engagement
            ),
        }

        return lifestyle_assessment

    def _calculate_work_life_balance(self, calendar_analysis: Dict[str, Any]) -> float:
        """
        Calculate work-life balance score based on calendar patterns.
        """
        event_types = calendar_analysis.get("event_distribution", {})

        # Assume 'work' events reduce balance, 'personal' events improve it
        work_events = event_types.get("work", 0)
        personal_events = event_types.get("personal", 0)
        total_events = sum(event_types.values())

        if total_events == 0:
            return 5.0  # Neutral score

        # Calculate balance (higher is better)
        balance_ratio = (personal_events + 1) / (work_events + 1)
        # Normalize to 0-10 scale
        balance_score = min(10, balance_ratio * 5)

        return round(balance_score, 2)

    def _calculate_activity_level(
        self, fitness_analysis: Dict[str, Any], location_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate physical activity level based on fitness and location data.
        """
        fitness_activities = fitness_analysis.get("total_activities", 0)
        location_visits = len(location_analysis.get("most_visited_locations", []))

        # Higher activity scores for more movement
        activity_score = min(10, (fitness_activities * 0.5) + (location_visits * 0.2))
        return round(activity_score, 2)

    def _calculate_social_engagement(self, calendar_analysis: Dict[str, Any]) -> float:
        """
        Calculate social engagement based on calendar events.
        """
        event_types = calendar_analysis.get("event_distribution", {})

        # Meetings, calls, and social events indicate engagement
        meetings = event_types.get("meetings", 0)
        social_events = sum(
            v
            for k, v in event_types.items()
            if "social" in k.lower() or "call" in k.lower()
        )

        engagement_score = min(10, (meetings * 0.3) + (social_events * 0.5))
        return round(engagement_score, 2)

    def _categorize_lifestyle(
        self, work_balance: float, activity_level: float, social_engagement: float
    ) -> str:
        """
        Categorize lifestyle based on scores.
        """
        avg_score = (work_balance + activity_level + social_engagement) / 3.0

        if avg_score >= 7.0:
            return "Balanced and Active"
        elif avg_score >= 5.0:
            return "Moderately Balanced"
        elif avg_score >= 3.0:
            return "Needs Improvement"
        else:
            return "Imbalanced"

    def _generate_behavioral_recommendations(
        self, patterns: Dict[str, Any]
    ) -> List[str]:
        """
        Generate personalized recommendations based on behavioral patterns.
        """
        recommendations = []

        # Look for improvement opportunities
        calendar_analysis = patterns["calendar_analysis"]
        fitness_analysis = patterns["fitness_analysis"]
        location_analysis = patterns["location_analysis"]

        # Fitness recommendations
        if fitness_analysis.get("consistency_rate_per_week", 0) < 3:
            recommendations.append(
                "Try to schedule 3-4 fitness sessions per week for better health outcomes."
            )

        # Schedule recommendations
        if calendar_analysis.get("total_events", 0) / 7.0 > 10:  # Avg >10 events/day
            recommendations.append(
                "Consider reducing meeting frequency to allow for focused work time."
            )

        # Location recommendations
        if len(location_analysis.get("most_visited_locations", [])) < 3:
            recommendations.append(
                "Explore new locations to break routine and stimulate creativity."
            )

        # Peak hour recommendations
        peak_hours = calendar_analysis.get("peak_hours", [])
        if len(peak_hours) >= 3:
            recommendations.append(
                f"You're most productive during hours {peak_hours[:3]}. Schedule important tasks during these times."
            )

        return (
            recommendations
            if recommendations
            else ["Your behavioral patterns look healthy and balanced!"]
        )


# Global instance for use in the application
daily_summarizer = DailySummarizer()
