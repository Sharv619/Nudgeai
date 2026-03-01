            content = file_data["content"]

            # Check for potential performance issues
            if (
                re.search(r"for.*in.*range\(.*\)", content)
                and len(re.findall(r"for.*in.*range\(.*\)", content)) > 2
            ):
                patterns_found.append(
                    {
                        "file": file_data["path"],
                        "pattern": "Multiple nested loops",
                        "description": "May indicate performance issues with algorithm complexity",
                    }
                )

            # Check for unoptimized list operations
            append_matches = re.findall(
                r"for.*?:\s*\n(\s+.+\.append\(.+\)\s*\n)+", content, re.MULTILINE
            )
            if len(append_matches) > 1:
                patterns_found.append(
                    {
                        "file": file_data["path"],
                        "pattern": "Frequent append operations in loops",
                        "description": "Consider using list comprehension or other methods for better performance",
                    }
                )

        # Process the pattern analysis with Hugging Face model to generate recommendations
        prompt = f"""
        Analyze the following codebase pattern analysis:
        Total files: {pattern_analysis["total_files"]}
        Total lines: {pattern_analysis["total_lines"]}
        Large files (>1KB): {len(pattern_analysis["large_files"])}
        Patterns found that may indicate optimization opportunities:
        {patterns_found[:10]}  # Show first 10 patterns
        
        Provide specific recommendations for:
        1. Code structure improvements
        2. Performance optimizations
        3. Refactoring opportunities
        4. Best practices to implement
        """

        ai_recommendations = _process_with_hf_model(prompt)

        return {
            "analysis": pattern_analysis,
            "patterns_found": patterns_found,
            "recommendations": ai_recommendations,
        }


def _register_resources(server: FastMCP):
    """Register resources that represent NudgeAI's data sources."""

    @server.resource("resource://calendar/availability/{date}")
    async def get_daily_availability(date: str) -> str:
        """
        Get calendar availability for a specific date.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            String representation of available time slots
        """
        logger.info(f"Getting calendar availability for {date}")
        # In practice, this would return actual calendar availability data
        return f"""
        Availability for {date}:
        - Morning (06:00-12:00): 3 hours free
        - Afternoon (12:00-18:00): 2 hours free (14:00-15:00 blocked)
        - Evening (18:00-24:00): 4 hours free
        """

    @server.resource("resource://habits/weekly-summary")
    async def get_weekly_habit_summary() -> str:
        """
        Get a summary of weekly habits and patterns.

        Returns:
            String representation of weekly habit summary
        """
        logger.info("Getting weekly habit summary")
        # In practice, this would analyze real data
        return """
        Weekly Habit Summary:
        Exercise: 4 days (target: 5) - 80% achievement
        Bedtime: Average 23:45 (target: 23:00) - Needs improvement
        Focus Hours: 28 hours (target: 30) - Close to target
        Hydration: Good consistency throughout the week
        """

    @server.resource("resource://upcoming-events")
    async def get_upcoming_events() -> str:
        """
        Get upcoming calendar events.

        Returns:
            String representation of upcoming events
        """
        logger.info("Getting upcoming events")
        # In practice, this would fetch from calendar API
        return """
        Upcoming Events:
        - Tomorrow 09:00-10:00: Team Standup
        - Tomorrow 14:00-15:00: Project Review
        - Wednesday 11:00-12:00: Doctor Appointment
        - Thursday 18:00-19:00: Gym Session
        """


def _register_prompts(server: FastMCP):
    """Register prompts that guide the LLM on how to interact with NudgeAI."""

    @server.prompt(
        name="proactive-nudge",
        description="Generate a proactive nudge based on user's data and context using Hugging Face models",
    )
    async def proactive_nudge(
        context: str, user_goals: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate a proactive nudge based on user's current context and goals using Hugging Face models.

        Args:
            context: Current context (time of day, location, calendar, etc.)
            user_goals: List of user's current goals

        Returns:
            List of message objects for the LLM
        """
        prompt = f"""
        Current context: {context}
        User goals: {", ".join(user_goals)}
        
        Based on this information, provide a helpful, encouraging nudge that motivates the user toward their goals.
        Be specific, actionable, and consider their current situation.
        Use a friendly, supportive tone that feels personal but professional.
        """

        ai_generated_nudge = _process_with_hf_model(prompt)

        return [
            {
                "role": "system",
                "content": "You are a proactive assistant that helps users achieve their goals by providing timely nudges based on their data and context.",
            },
            {"role": "user", "content": ai_generated_nudge},
        ]


def main():
    """Main entry point for the NudgeAI MCP server."""
    server = create_nudgeai_mcp_server()

    print("Starting NudgeAI MCP Server with Hugging Face Integration...")
    print(f"Using model: {HF_MODEL}")
    print("Connect to this server using an MCP-compatible client.")
    print("Press Ctrl+C to stop the server.")

    try:
        # Run the server using stdio transport (default for MCP)
        server.run(transport="stdio")
    except KeyboardInterrupt:
        print("\nShutting down NudgeAI MCP Server...")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        raise


if __name__ == "__main__":
    main()
