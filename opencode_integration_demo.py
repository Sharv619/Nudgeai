#!/usr/bin/env python3
"""
Opencode Integration Demo with NudgeAI MCP Server
This script demonstrates how Opencode can integrate with the NudgeAI MCP server
to provide enhanced personal assistance capabilities.
"""

import asyncio
from mcp_client_connector import OpencodeMCPConnector


class OpencodeNudgeAIIntegration:
    """
    Class that represents the integration between Opencode and NudgeAI.
    This would typically be incorporated into the Opencode core system.
    """

    def __init__(self):
        self.connector = OpencodeMCPConnector()
        self.is_active = False

    async def activate_integration(self):
        """
        Activate the integration with the NudgeAI MCP server.
        """
        print("Activating Opencode-NudgeAI integration...")
        self.is_active = True
        print("✓ Opencode is now integrated with NudgeAI MCP server")

    async def get_context_aware_assistance(self, context: str, user_goals: list):
        """
        Get context-aware assistance from NudgeAI based on current situation and goals.

        Args:
            context: Current context (time, location, calendar events, etc.)
            user_goals: List of user's current goals

        Returns:
            Dict with assistance and recommendations
        """
        if not self.is_active:
            await self.activate_integration()

        print(f"\n--- Getting Context-Aware Assistance ---")
        print(f"Context: {context}")
        print(f"Goals: {user_goals}")

        # Generate a proactive nudge based on context and goals
        nudge_result = await self.connector.generate_proactive_nudge(
            context, user_goals
        )

        # Also get relevant calendar info
        availability = await self.connector.get_calendar_availability("2024-01-22")
        upcoming = await self.connector.get_upcoming_events()

        return {
            "nudge": nudge_result,
            "calendar_availability": availability.strip(),
            "upcoming_events": upcoming.strip(),
            "status": "success",
        }

    async def analyze_user_patterns(
        self, data_sources: list = None, focus_areas: list = None
    ):
        """
        Analyze user patterns across different data sources.

        Args:
            data_sources: List of data sources to analyze
            focus_areas: Specific areas to focus on

        Returns:
            Analysis of user patterns and insights
        """
        if not self.is_active:
            await self.activate_integration()

        if data_sources is None:
            data_sources = ["calendar", "location", "drive"]
        if focus_areas is None:
            focus_areas = ["productivity", "health", "work-life balance"]

        print(f"\n--- Analyzing User Patterns ---")
        print(f"Data sources: {data_sources}")
        print(f"Focus areas: {focus_areas}")

        # Get personal insights
        insights = await self.connector.call_mcp_tool(
            "get_personal_insights",
            {"data_sources": data_sources, "focus_areas": focus_areas},
        )

        # Get habit analysis
        habits = await self.connector.call_mcp_tool(
            "analyze_habits", {"time_period": "week", "focus_area": "overall"}
        )

        return {
            "personal_insights": insights,
            "habit_analysis": habits,
            "status": "success",
        }

    async def search_and_summarize_documents(self, query: str, max_results: int = 5):
        """
        Search through user's documents and provide AI-generated summaries.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            Search results with AI summaries
        """
        if not self.is_active:
            await self.activate_integration()

        print(f"\n--- Searching Documents ---")
        print(f"Query: {query}")

        # Query drive documents
        results = await self.connector.call_mcp_tool(
            "query_drive_documents", {"query": query, "max_results": max_results}
        )

        return {
            "documents": results.get("documents", []),
            "summary": results.get("summary", ""),
            "count": results.get("count", 0),
            "status": "success",
        }

    async def check_calendar_and_schedule(
        self, start_date: str, end_date: str, event_type: str = None
    ):
        """
        Check calendar availability and get AI insights on scheduling.

        Args:
            start_date: Start date to check
            end_date: End date to check
            event_type: Optional event type filter

        Returns:
            Calendar events with AI analysis
        """
        if not self.is_active:
            await self.activate_integration()

        print(f"\n--- Checking Calendar Availability ---")
        print(f"Date range: {start_date} to {end_date}")
        if event_type:
            print(f"Event type: {event_type}")

        # Query calendar
        results = await self.connector.call_mcp_tool(
            "query_calendar",
            {"start_date": start_date, "end_date": end_date, "event_type": event_type},
        )

        return {
            "events": results.get("events", []),
            "insights": results.get("insights", ""),
            "summary": results.get("summary", ""),
            "status": "success",
        }


async def main():
    """
    Demonstrate the Opencode-NudgeAI integration capabilities.
    """
    print("🎯 Opencode - NudgeAI MCP Integration Demo")
    print("=" * 50)

    # Initialize the integration
    integration = OpencodeNudgeAIIntegration()
    await integration.activate_integration()

    # Example 1: Context-aware assistance
    print("\n📝 Example 1: Context-Aware Assistance")
    assistance = await integration.get_context_aware_assistance(
        context="It's Tuesday afternoon and you have completed most of your planned tasks. Your calendar shows free time from 3-5 PM.",
        user_goals=[
            "exercise regularly",
            "learn new skills",
            "maintain work-life balance",
        ],
    )
    print(f"✓ Received assistance with {len(assistance['nudge'])} nudge(s)")

    # Example 2: Pattern analysis
    print("\n📊 Example 2: Pattern Analysis")
    patterns = await integration.analyze_user_patterns(
        data_sources=["calendar", "location"], focus_areas=["productivity", "health"]
    )
    print(f"✓ Completed pattern analysis")

    # Example 3: Document search
    print("\n🔍 Example 3: Document Search")
    documents = await integration.search_and_summarize_documents(
        query="project timeline", max_results=3
    )
    print(f"✓ Found {documents['count']} document(s)")

    # Example 4: Calendar check
    print("\n📅 Example 4: Calendar Check")
    calendar_check = await integration.check_calendar_and_schedule(
        start_date="2024-01-22", end_date="2024-01-26", event_type="meeting"
    )
    print(f"✓ Calendar checked, found {len(calendar_check['events'])} event(s)")

    print("\n" + "=" * 50)
    print("✅ Opencode is now successfully integrated with NudgeAI!")
    print("\nBenefits of this integration:")
    print("• Context-aware personal assistance")
    print("• AI-powered insights on your data")
    print("• Proactive nudges toward your goals")
    print("• Intelligent document search and summarization")
    print("• Calendar optimization recommendations")
    print("• Habit tracking with personalized advice")

    print(f"\n💡 The integration is ready to enhance Opencode's capabilities")
    print("   with NudgeAI's personal assistance features!")


if __name__ == "__main__":
    asyncio.run(main())
