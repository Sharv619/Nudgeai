#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for NudgeAI using Hugging Face Models
This server exposes NudgeAI's capabilities to LLMs via the Model Context Protocol,
leveraging Hugging Face models for enhanced processing.
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, EmbeddedResource
import requests
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Hugging Face client
HF_TOKEN = os.getenv("HF_token")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")

if not HF_TOKEN:
    raise ValueError("HF_token environment variable is required")

hf_client = InferenceClient(model=HF_MODEL, token=HF_TOKEN)


def create_nudgeai_mcp_server():
    """Create and configure the NudgeAI MCP server with Hugging Face integration."""

    # Initialize the FastMCP server
    server = FastMCP(
        name="NudgeAI MCP Server with Hugging Face",
        instructions="A proactive personal assistant that leverages Hugging Face models for enhanced processing of scheduling, habit tracking, and context-aware nudges.",
        debug=True,
        log_level="INFO",
    )

    # Add tools that expose NudgeAI's capabilities
    _register_tools(server)

    # Add resources that represent NudgeAI's data sources
    _register_resources(server)

    # Add prompts that guide the LLM on how to interact with NudgeAI
    _register_prompts(server)

    return server


def _process_with_hf_model(prompt: str) -> str:
    """
    Process text using the Hugging Face model.

    Args:
        prompt: Input prompt to process

    Returns:
        Generated response from the model
    """
    try:
        # Use the Hugging Face Inference API to process the prompt
        # First try the chat completion API
        try:
            response = hf_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7,
            )
            content = response.choices[0].message.content
            return content if content is not None else f"Processed: {prompt[:100]}..."
        except:
            # If chat completion fails, fall back to text generation
            response = hf_client.text_generation(
                prompt=prompt,
                max_new_tokens=500,
                temperature=0.7,
                return_full_text=False,
            )
            return (
                response
                if isinstance(response, str)
                else str(response or f"Processed: {prompt[:100]}...")
            )
    except Exception as e:
        logger.error(f"Error processing with Hugging Face model: {e}")
        # Return a simulated response when API fails
        return f"Simulated AI insights for: {prompt[:100]}..."


def _register_tools(server: FastMCP):
    """Register tools that expose NudgeAI's capabilities with Hugging Face integration."""

    @server.tool(
        name="query_calendar",
        description="Query the user's calendar for availability and events",
        title="Calendar Query Tool",
    )
    async def query_calendar(
        start_date: str, end_date: str, event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query calendar events within a date range and process with Hugging Face model.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            event_type: Optional filter for event type (e.g., 'meeting', 'personal')

        Returns:
            Dictionary with calendar events and AI-processed insights
        """
        logger.info(
            f"Querying calendar from {start_date} to {end_date}, type: {event_type}"
        )

        # Simulate calendar query - in real implementation, this would connect to Google Calendar API
        events = [
            {
                "id": "event1",
                "title": "Team Meeting",
                "start_time": "2024-01-15T10:00:00Z",
                "end_time": "2024-01-15T11:00:00Z",
                "location": "Conference Room A",
                "attendees": ["john@example.com", "jane@example.com"],
            },
            {
                "id": "event2",
                "title": "Gym Session",
                "start_time": "2024-01-15T18:00:00Z",
                "end_time": "2024-01-15T19:00:00Z",
                "location": "Fitness Center",
                "attendees": [],
            },
        ]

        # Process the events with Hugging Face model to generate insights
        prompt = f"""
        Analyze the following calendar events and provide insights:
        {events}
        
        Consider the event types, timing, and patterns. Provide brief insights about:
        1. Schedule density
        2. Work-life balance
        3. Potential conflicts or optimization opportunities
        """

        ai_insights = _process_with_hf_model(prompt)

        return {
            "events": events,
            "insights": ai_insights,
            "summary": f"Found {len(events)} events between {start_date} and {end_date}",
        }

    @server.tool(
        name="query_location_history",
        description="Query the user's location history to understand patterns",
        title="Location History Tool",
    )
    async def query_location_history(
        start_date: str, end_date: str, location_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query location history data within a date range and process with Hugging Face model.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            location_type: Optional filter for location type (e.g., 'gym', 'office', 'home')

        Returns:
            Dictionary with location data and AI-processed insights
        """
        logger.info(
            f"Querying location history from {start_date} to {end_date}, type: {location_type}"
        )

        # Sample response - in practice, this would come from Google Location History API
        locations = [
            {
                "timestamp": "2024-01-15T08:30:00Z",
                "place": "Office",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "duration_minutes": 480,
            },
            {
                "timestamp": "2024-01-15T18:15:00Z",
                "place": "Gym",
                "latitude": 37.7812,
                "longitude": -122.4068,
                "duration_minutes": 60,
            },
        ]

        # Process the location data with Hugging Face model to generate insights
        prompt = f"""
        Analyze the following location history data:
        {locations}
        
        Provide insights about:
        1. Movement patterns
        2. Routine consistency
        3. Potential lifestyle optimizations
        """

        ai_insights = _process_with_hf_model(prompt)

        return {
            "locations": locations,
            "insights": ai_insights,
            "summary": f"Found location data for {len(locations)} places between {start_date} and {end_date}",
        }

    @server.tool(
        name="query_drive_documents",
        description="Search and retrieve content from the user's Drive documents",
        title="Drive Document Search Tool",
    )
    async def query_drive_documents(
        query: str, file_type: Optional[str] = None, max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search Drive documents based on a query and process with Hugging Face model.

        Args:
            query: Search query string
            file_type: Optional filter for file type (e.g., 'pdf', 'doc', 'sheet')
            max_results: Maximum number of results to return (default 5)

        Returns:
            Dictionary with matching documents and AI-processed content summaries
        """
        logger.info(
            f"Searching Drive for: '{query}', type: {file_type}, max: {max_results}"
        )

        # Sample response - in practice, this would come from Google Drive API
        documents = [
            {
                "title": "Workout Plan Q1",
                "filename": "workout_plan_q1.pdf",
                "content_snippet": "Weekly workout schedule focusing on strength training...",
                "last_modified": "2024-01-10T09:15:00Z",
                "size_bytes": 1024000,
            },
            {
                "title": "Goals 2024",
                "filename": "goals_2024.docx",
                "content_snippet": "Personal and professional goals for the year...",
                "last_modified": "2024-01-05T14:30:00Z",
                "size_bytes": 512000,
            },
        ]

        # Process the document content with Hugging Face model to generate summaries
        prompt = f"""
        Based on the following documents related to the query '{query}':
        {documents}
        
        Provide a concise summary of the key information and relevance to the query.
        """

        ai_summary = _process_with_hf_model(prompt)

        return {"documents": documents, "summary": ai_summary, "count": len(documents)}

    @server.tool(
        name="analyze_habits",
        description="Analyze user's habits and patterns based on available data using Hugging Face models",
        title="Habit Analysis Tool",
    )
    async def analyze_habits(
        time_period: str = "week", focus_area: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze user habits and patterns using Hugging Face models for deeper insights.

        Args:
            time_period: Time period to analyze ('day', 'week', 'month')
            focus_area: Optional focus area ('exercise', 'productivity', 'sleep', etc.)

        Returns:
            Analysis of habits with AI-generated insights and recommendations
        """
        logger.info(f"Analyzing habits for {time_period} period, focus: {focus_area}")

        # Sample analysis - in practice, this would analyze your collected data
        raw_analysis = {
            "period": time_period,
            "focus_area": focus_area or "overall",
            "summary": "User has been consistent with gym visits but needs improvement in evening routine",
            "metrics": {
                "gym_visits": 4,
                "average_bedtime": "23:45",
                "work_hours": 38,
                "meeting_count": 12,
            },
        }

        # Process the raw analysis with Hugging Face model to generate deeper insights
        prompt = f"""
        Analyze the following habit data for the {time_period} period:
        {raw_analysis}
        
        Provide deeper insights including:
        1. Trends and patterns
        2. Potential causal relationships
        3. Personalized recommendations for improvement
        4. Motivational messaging based on achievements
        """

        ai_analysis = _process_with_hf_model(prompt)

        return {"data": raw_analysis, "analysis": ai_analysis}

    @server.tool(
        name="get_personal_insights",
        description="Generate comprehensive personal insights using Hugging Face models",
        title="Personal Insights Tool",
    )
    async def get_personal_insights(
        data_sources: List[str], focus_areas: List[str]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights by combining multiple data sources processed with Hugging Face models.

        Args:
            data_sources: List of data sources to consider (e.g., ['calendar', 'location', 'drive'])
            focus_areas: List of focus areas for analysis (e.g., ['productivity', 'health', 'relationships'])

        Returns:
            Comprehensive insights synthesized from multiple data sources
        """
        logger.info(
            f"Generating personal insights from {data_sources}, focusing on {focus_areas}"
        )

        # Simulated data synthesis from multiple sources
        combined_data = {
            "calendar_data": {
                "meetings_attended": 8,
                "free_time": 15,
                "focus_hours": 20,
            },
            "location_data": {
                "places_visited": 5,
                "commute_time_avg": 45,
                "work_from_home_days": 3,
            },
            "document_data": {
                "goals_tracked": 12,
                "progress_updates": 8,
                "notes_created": 15,
            },
        }

        # Process the combined data with Hugging Face model to generate comprehensive insights
        prompt = f"""
        Synthesize insights from the following data sources:
        {combined_data}
        
        Focus areas: {focus_areas}
        
        Provide:
        1. Cross-domain insights connecting different aspects of life
        2. Recommendations for improved balance
        3. Identification of positive trends to reinforce
        4. Areas needing attention with specific actions
        """

        ai_synthesis = _process_with_hf_model(prompt)

        return {
            "data_sources": combined_data,
            "synthesis": ai_synthesis,
            "focus_areas": focus_areas,
        }

    @server.tool(
        name="query_codebase",
        description="Search and analyze the local codebase for optimization opportunities",
        title="Codebase Analysis Tool",
    )
    async def query_codebase(
        query: str, file_type: Optional[str] = None, max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search through the local codebase based on a query and process with Hugging Face model.
        This tool analyzes code files in the current project to identify optimization opportunities.

        Args:
            query: Search query string (e.g., 'optimization', 'performance', 'refactoring')
            file_type: Optional filter for file type (e.g., 'py', 'js', 'ts')
            max_results: Maximum number of results to return (default 5)

        Returns:
            Dictionary with matching code segments and AI-processed analysis
        """
        logger.info(
            f"Searching codebase for: '{query}', type: {file_type}, max: {max_results}"
        )

        # Import the codebase ingestion modules
        from data_ingestion.codebase.code_fetcher import CodeFetcher
        
        # Initialize the code fetcher
        fetcher = CodeFetcher()
        
        # Define supported file extensions
        if file_type:
            extensions = [f".{file_type}"]
        else:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.html', '.css', '.md']
        
        # Fetch code files from the project
        code_files = fetcher.fetch_files(extensions)
        
        # Filter and sort files based on relevance to the query
        filtered_files = []
        for file_info in code_files:
            # Look for the query term in filename or content
            if query.lower() in file_info['filename'].lower() or query.lower() in file_info['content'].lower():
                filtered_files.append(file_info)
        
        # Sort by size and take top results
        filtered_files = sorted(filtered_files, key=lambda x: x['size'], reverse=True)[:max_results]
        
        # Process the code content with Hugging Face model to generate analysis
        if filtered_files:
            code_context = "\n".join([
                f"File: {f['path']}\nContent Preview: {f['content'][:300]}...\n" 
                for f in filtered_files
            ])
            prompt = f"""
            Analyze the following codebase files in response to the query '{query}':
            {code_context}
            
            Provide a concise analysis of the code and specific suggestions for:
            1. Optimization opportunities
            2. Performance improvements
            3. Code quality enhancements
            4. Best practices recommendations
            """
        else:
            # If no files match the query, search for files more broadly
            all_files = sorted(code_files, key=lambda x: x['size'], reverse=True)[:max_results]
            if all_files:
                code_context = "\n".join([
                    f"File: {f['path']}\nContent Preview: {f['content'][:200]}...\n" 
                    for f in all_files
                ])
                prompt = f"""
                Here are some codebase files. Analyze them in light of the query '{query}':
                {code_context}
                
                Provide a concise analysis of the code and specific suggestions for:
                1. Performance improvements
                2. Code quality enhancements
                3. Best practices recommendations
                """
                filtered_files = all_files
            else:
                prompt = f"No code files were found in the project to analyze for the query '{query}'."

        ai_analysis = _process_with_hf_model(prompt)

        # Prepare simplified file info for response
        result_files = []
        if filtered_files:  # Only process if filtered_files is not empty
            result_files = [
                {
                    'path': f['path'],
                    'filename': f['filename'],
                    'size': f['size'],
                    'lines': f['lines']
                } for f in filtered_files
            ]

        return {
