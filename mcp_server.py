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

# Import RAG system components
from ragsystem.mcp_integration import rag_mcp_integrator
from ragsystem.location_nudger import location_nudger
from ragsystem.pattern_analyzer import pattern_analyzer
from ragsystem.daily_summarizer import daily_summarizer

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

# WhiteCircle API Configuration
WHITECIRCLE_API_KEY = os.getenv("WHITECIRCLE_API_KEY")
WHITECIRCLE_URL = "https://api.whitecircle.ai/v1/check"


def check_with_whitecircle(text: str):
    """
    Check text with WhiteCircle for quality assurance and hallucination detection.

    Args:
        text: Text to check with WhiteCircle

    Returns:
        Tuple of (is_valid: bool, reason_or_none: str or None)
    """
    if not WHITECIRCLE_API_KEY:
        # If no API key, bypass the check (development mode)
        logger.warning("WHITECIRCLE_API_KEY not set, bypassing quality check")
        return True, None

    try:
        response = requests.post(
            WHITECIRCLE_URL,
            json={
                "input": text,
                "deployment": "nudge-ai-production",
                "policies": ["hallucination_filter", "quality_check"],
            },
            headers={"Authorization": f"Bearer {WHITECIRCLE_API_KEY}"},
            timeout=10,  # 10 second timeout
        )
        response.raise_for_status()
        result = response.json()

        # If a policy is triggered (violated)
        if result.get("flagged"):
            return False, result.get("reason", "Content flagged by WhiteCircle policy")
        return True, None
    except requests.exceptions.RequestException as e:
        logger.error(f"WhiteCircle API error: {e}")
        # In case of API failure, we'll let the content through but log the error
        return True, None
    except Exception as e:
        logger.error(f"Unexpected error with WhiteCircle: {e}")
        return True, None


def create_nudgeai_mcp_server():
    """Create and configure the NudgeAI MCP server with Hugging Face integration."""

    # Initialize the FastMCP server
    server = FastMCP(
        name="NudgeAI MCP Server with Hugging Face and WhiteCircle Integration",
        instructions="A proactive personal assistant that leverages Hugging Face models for enhanced processing of scheduling, habit tracking, and context-aware nudges. Features WhiteCircle quality gates to prevent hallucinations and ensure high-quality, factually-grounded responses through automated quality checks and retry mechanisms.",
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


def _process_with_hf_model(prompt: str, enforce_quality: bool = True) -> str:
    """
    Process text using the Hugging Face model with optional WhiteCircle quality enforcement.

    Args:
        prompt: Input prompt to process
        enforce_quality: Whether to enforce WhiteCircle quality check

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
            result = content if content is not None else f"Processed: {prompt[:100]}..."
        except Exception as chat_error:
            logger.warning(
                f"Chat completion failed: {chat_error}, falling back to text generation"
            )
            # If chat completion fails, fall back to text generation
            try:
                response = hf_client.text_generation(
                    prompt=prompt,
                    max_new_tokens=500,
                    temperature=0.7,
                    return_full_text=False,
                )
                result = (
                    response
                    if isinstance(response, str)
                    else str(response or f"Processed: {prompt[:100]}...")
                )
            except Exception as text_gen_error:
                logger.error(f"Text generation also failed: {text_gen_error}")
                # If both methods fail, return a simulated response
                return f"Simulated AI insights for: {prompt[:100]}..."

        # If quality enforcement is enabled, check with WhiteCircle
        if enforce_quality:
            is_valid, error = check_with_whitecircle(result)

            if not is_valid:
                # If flagged by WhiteCircle, return a special response prompting regeneration
                logger.warning(f"WhiteCircle flagged content: {error}")
                return f"WhiteCircle Quality Gate: {error}. Response needs regeneration with stricter fact-checking."

        return result
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
        Query calendar events within a date range and return direct JSON data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            event_type: Optional filter for event type (e.g., 'meeting', 'personal')

        Returns:
            Dictionary with calendar events and direct JSON data
        """
        logger.info(
            f"Querying calendar from {start_date} to {end_date}, type: {event_type}"
        )

        # Load calendar data directly from sync file
        import json
        import os
        from datetime import datetime

        calendar_file = "data_sync/calendar_sync.json"
        events = []

        try:
            if os.path.exists(calendar_file):
                with open(calendar_file, "r") as f:
                    calendar_data = json.load(f)

                # Parse date range
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")

                # Filter events by date range
                for item in calendar_data:
                    metadata = item.get("metadata", {})
                    start_time = metadata.get("start_time", "")

                    if start_time:
                        try:
                            event_dt = datetime.fromisoformat(
                                start_time.replace("Z", "+00:00")
                            )
                            # Convert to naive datetime for comparison
                            event_dt = event_dt.replace(tzinfo=None)

                            if start_dt <= event_dt <= end_dt:
                                # Apply event type filter if specified
                                if event_type:
                                    title = metadata.get(
                                        "summary", metadata.get("title", "")
                                    ).lower()
                                    if event_type.lower() not in title:
                                        continue

                                events.append(
                                    {
                                        "id": metadata.get("id", item.get("id", "")),
                                        "title": metadata.get(
                                            "summary", metadata.get("title", "No title")
                                        ),
                                        "start_time": metadata.get("start_time", ""),
                                        "end_time": metadata.get("end_time", ""),
                                        "location": metadata.get("location", ""),
                                        "attendees": metadata.get("attendees", []),
                                        "description": metadata.get("description", ""),
                                        "synced_at": metadata.get("synced_at", ""),
                                    }
                                )
                        except ValueError:
                            continue
        except Exception as e:
            logger.error(f"Error reading calendar data: {e}")

        # Return direct JSON data without AI processing
        return {
            "events": events,
            "insights": f"Direct JSON data for {len(events)} calendar events between {start_date} and {end_date}",
            "summary": f"Found {len(events)} events between {start_date} and {end_date}",
            "data_source": "direct_json",
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
        Query location history data within a date range and return direct JSON data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            location_type: Optional filter for location type (e.g., 'gym', 'office', 'home')

        Returns:
            Dictionary with location data and direct JSON data
        """
        logger.info(
            f"Querying location history from {start_date} to {end_date}, type: {location_type}"
        )

        # Load location data directly from sync file
        import json
        import os
        from datetime import datetime

        location_file = "data_sync/location_sync.json"
        locations = []

        try:
            if os.path.exists(location_file):
                with open(location_file, "r") as f:
                    location_data = json.load(f)

                # Parse date range
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")

                # Filter locations by date range
                for item in location_data:
                    metadata = item.get("metadata", {})
                    timestamp = metadata.get("timestamp", "")

                    if timestamp:
                        try:
                            event_dt = datetime.fromisoformat(
                                timestamp.replace("Z", "+00:00")
                            )
                            # Convert to naive datetime for comparison
                            event_dt = event_dt.replace(tzinfo=None)

                            if start_dt <= event_dt <= end_dt:
                                # Apply location type filter if specified
                                if location_type:
                                    loc_type = metadata.get("location_type", "").lower()
                                    if location_type.lower() != loc_type:
                                        continue

                                locations.append(
                                    {
                                        "id": metadata.get("id", item.get("id", "")),
                                        "timestamp": metadata.get("timestamp", ""),
                                        "place": metadata.get("place_name", ""),
                                        "location_type": metadata.get(
                                            "location_type", ""
                                        ),
                                        "latitude": metadata.get("latitude"),
                                        "longitude": metadata.get("longitude"),
                                        "accuracy": metadata.get("accuracy", ""),
                                        "synced_at": metadata.get("synced_at", ""),
                                    }
                                )
                        except ValueError:
                            continue
        except Exception as e:
            logger.error(f"Error reading location data: {e}")

        # Return direct JSON data without AI processing
        return {
            "locations": locations,
            "insights": f"Direct JSON data for {len(locations)} location visits between {start_date} and {end_date}",
            "summary": f"Found {len(locations)} location visits between {start_date} and {end_date}",
            "data_source": "direct_json",
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

        # Use semantic search to find relevant documents
        filters = {"type": "document"}
        if file_type:
            # For now, we just add the file type as a filter if it exists in metadata
            if file_type in ["pdf", "doc", "docx", "sheet", "xls", "xlsx"]:
                filters["file_type"] = file_type

        semantic_results = rag_mcp_integrator.semantic_search(
            query, k=max_results, filters=filters
        )

        # Convert semantic results to the expected format
        documents = []
        for result in semantic_results:
            metadata = result["document"]["metadata"]
            documents.append(
                {
                    "id": result["document"]["id"],
                    "title": metadata.get("name", metadata.get("title", "Untitled")),
                    "filename": metadata.get(
                        "filename", metadata.get("name", "Unknown")
                    ),
                    "content_snippet": result["document"]["text"][:200] + "..."
                    if len(result["document"]["text"]) > 200
                    else result["document"]["text"],
                    "last_modified": metadata.get(
                        "modifiedTime", metadata.get("synced_at", "Unknown")
                    ),
                    "size_bytes": metadata.get("size", 0),
                    "similarity_score": result.get("similarity_score", 0.0),
                }
            )

        # Process the document content with Hugging Face model to generate summaries
        if documents:
            prompt = f"""
            Based on the following documents related to the query '{query}':
            {documents}
            
            Provide a concise summary of the key information and relevance to the query.
            Highlight the most important findings and how they relate to the user's needs.
            """
        else:
            prompt = f"No documents found matching the query '{query}'. Try refining your search terms or checking if documents exist."

        ai_summary = _process_with_hf_model(prompt, enforce_quality=True)

        return {"documents": documents, "summary": ai_summary, "count": len(documents)}

    @server.tool(
        name="analyze_habits",
        description="Analyze user's habits and patterns based on available data",
        title="Habit Analysis Tool",
    )
    async def analyze_habits(
        time_period: str = "week", focus_area: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze user habits and patterns using direct JSON data from sync files.

        Args:
            time_period: Time period to analyze ('day', 'week', 'month')
            focus_area: Optional focus area ('exercise', 'productivity', 'sleep', etc.)

        Returns:
            Analysis of habits with direct JSON data
        """
        logger.info(f"Analyzing habits for {time_period} period, focus: {focus_area}")

        # Load data directly from sync files
        import json
        import os
        from datetime import datetime, timedelta

        # Map time period to number of days
        period_map = {"day": 1, "week": 7, "month": 30}
        days = period_map.get(time_period, 7)

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Load fitness data
        fitness_activities = []
        fitness_file = "data_sync/fit_sync.json"
        try:
            if os.path.exists(fitness_file):
                with open(fitness_file, "r") as f:
                    fitness_data = json.load(f)

                for item in fitness_data:
                    metadata = item.get("metadata", {})
                    timestamp = metadata.get("timestamp", "")

                    if timestamp:
                        try:
                            event_dt = datetime.fromisoformat(
                                timestamp.replace("Z", "+00:00")
                            )
                            # Convert to naive datetime for comparison
                            event_dt = event_dt.replace(tzinfo=None)

                            if start_date <= event_dt <= end_date:
                                fitness_activities.append(metadata)
                        except ValueError:
                            continue
        except Exception as e:
            logger.error(f"Error reading fitness data: {e}")

        # Load calendar data
        calendar_events = []
        calendar_file = "data_sync/calendar_sync.json"
        try:
            if os.path.exists(calendar_file):
                with open(calendar_file, "r") as f:
                    calendar_data = json.load(f)

                for item in calendar_data:
                    metadata = item.get("metadata", {})
                    start_time = metadata.get("start_time", "")

                    if start_time:
                        try:
                            event_dt = datetime.fromisoformat(
                                start_time.replace("Z", "+00:00")
                            )
                            # Convert to naive datetime for comparison
                            event_dt = event_dt.replace(tzinfo=None)

                            if start_date <= event_dt <= end_date:
                                calendar_events.append(metadata)
                        except ValueError:
                            continue
        except Exception as e:
            logger.error(f"Error reading calendar data: {e}")

        # Load location data
        location_visits = []
        location_file = "data_sync/location_sync.json"
        try:
            if os.path.exists(location_file):
                with open(location_file, "r") as f:
                    location_data = json.load(f)

                for item in location_data:
                    metadata = item.get("metadata", {})
                    timestamp = metadata.get("timestamp", "")

                    if timestamp:
                        try:
                            event_dt = datetime.fromisoformat(
                                timestamp.replace("Z", "+00:00")
                            )
                            # Convert to naive datetime for comparison
                            event_dt = event_dt.replace(tzinfo=None)

                            if start_date <= event_dt <= end_date:
                                location_visits.append(metadata)
                        except ValueError:
                            continue
        except Exception as e:
            logger.error(f"Error reading location data: {e}")

        # Compile analysis from the gathered data
        raw_analysis = {
            "period": time_period,
            "focus_area": focus_area or "overall",
            "summary": f"Analysis based on {len(fitness_activities)} fitness activities, {len(calendar_events)} calendar events, and {len(location_visits)} location visits",
            "metrics": {
                "fitness_activities_count": len(fitness_activities),
                "calendar_events_count": len(calendar_events),
                "location_visits_count": len(location_visits),
                "exercise_frequency": len(
                    [
                        fa
                        for fa in fitness_activities
                        if "walk" in fa.get("activity_type", "").lower()
                        or "gym" in fa.get("activity_type", "").lower()
                    ]
                ),
                "work_related_events": len(
                    [
                        ce
                        for ce in calendar_events
                        if "meeting" in ce.get("summary", "").lower()
                        or "work" in ce.get("summary", "").lower()
                    ]
                ),
                "total_steps": sum(fa.get("steps", 0) for fa in fitness_activities),
                "total_calories": sum(
                    fa.get("calories", 0) for fa in fitness_activities
                ),
                "total_duration": sum(
                    fa.get("duration_minutes", 0) for fa in fitness_activities
                ),
            },
            "data_source": "direct_json",
        }

        return {
            "data": raw_analysis,
            "analysis": f"Direct JSON analysis for {time_period} period with {len(fitness_activities)} fitness activities, {len(calendar_events)} calendar events, and {len(location_visits)} location visits",
        }

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

        # Use semantic search to gather relevant data from specified sources
        combined_data = {}

        for source in data_sources:
            if source == "calendar":
                calendar_results = rag_mcp_integrator.semantic_search(
                    f"calendar events for {', '.join(focus_areas)}",
                    k=10,
                    filters={"type": "calendar_event"},
                )
                combined_data["calendar_data"] = {
                    "events": [r["document"]["metadata"] for r in calendar_results],
                    "event_count": len(calendar_results),
                    "focus_area_matches": len(
                        [
                            r
                            for r in calendar_results
                            if any(
                                area.lower()
                                in r["document"]["metadata"].get("summary", "").lower()
                                for area in focus_areas
                            )
                        ]
                    ),
                }

            elif source == "location":
                location_results = rag_mcp_integrator.semantic_search(
                    f"location visits for {', '.join(focus_areas)}",
                    k=10,
                    filters={"type": "location"},
                )
                combined_data["location_data"] = {
                    "visits": [r["document"]["metadata"] for r in location_results],
                    "visit_count": len(location_results),
                    "focus_area_matches": len(
                        [
                            r
                            for r in location_results
                            if any(
                                area.lower()
                                in r["document"]["metadata"]
                                .get("place_name", "")
                                .lower()
                                for area in focus_areas
                            )
                        ]
                    ),
                }

            elif source == "drive":
                document_results = rag_mcp_integrator.semantic_search(
                    f"documents for {', '.join(focus_areas)}",
                    k=10,
                    filters={"type": "document"},
                )
                combined_data["document_data"] = {
                    "documents": [r["document"]["metadata"] for r in document_results],
                    "document_count": len(document_results),
                    "focus_area_matches": len(
                        [
                            r
                            for r in document_results
                            if any(
                                area.lower() in r["document"]["text"].lower()
                                for area in focus_areas
                            )
                        ]
                    ),
                }

        # Process the combined data with Hugging Face model to generate comprehensive insights
        if combined_data:
            prompt = f"""
            Synthesize insights from the following data sources:
            {combined_data}
            
            Focus areas: {focus_areas}
            
            Provide:
            1. Cross-domain insights connecting different aspects of life
            2. Recommendations for improved balance
            3. Identification of positive trends to reinforce
            4. Areas needing attention with specific actions
            5. Correlations between different data sources that might impact the focus areas
            """
        else:
            prompt = f"No data found for sources {data_sources} related to focus areas {focus_areas}. This might indicate that data hasn't been synced yet or search terms need refinement."

        ai_synthesis = _process_with_hf_model(prompt, enforce_quality=True)

        return {
            "data_sources": combined_data,
            "synthesis": ai_synthesis,
            "focus_areas": focus_areas,
        }

    @server.tool(
        name="semantic_search_all_data",
        description="Perform semantic search across all indexed user data",
        title="Universal Semantic Search Tool",
    )
    async def semantic_search_all_data(
        query: str, data_filters: Optional[List[str]] = None, max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Perform semantic search across all indexed user data including calendar, location, fitness, and documents.

        Args:
            query: Natural language search query
            data_filters: Optional list of data types to include (e.g., ['calendar', 'location'])
            max_results: Maximum number of results to return (default 5)

        Returns:
            Dictionary with semantic search results and relevance scores
        """
        logger.info(
            f"Performing semantic search for: '{query}', filters: {data_filters}, max: {max_results}"
        )

        # Determine filters based on data_filters parameter
        filters = {}
        if data_filters:
            # Map data filter names to the actual type values stored in the RAG system
            type_mapping = {
                "calendar": "calendar_event",
                "location": "location",
                "fit": "fitness_activity",
                "fitness": "fitness_activity",
                "drive": "document",
                "document": "document",
            }
            mapped_types = [
                type_mapping.get(df, df) for df in data_filters if df in type_mapping
            ]
            if mapped_types:
                filters["type"] = mapped_types

        # Perform semantic search using the RAG system
        semantic_results = rag_mcp_integrator.semantic_search(
            query, k=max_results, filters=filters
        )

        # Format results
        formatted_results = []
        for result in semantic_results:
            formatted_results.append(
                {
                    "id": result["document"]["id"],
                    "text": result["document"]["text"],
                    "metadata": result["document"]["metadata"],
                    "similarity_score": result["similarity_score"],
                    "source_type": result["document"]["metadata"].get(
                        "type", "unknown"
                    ),
                }
            )

        return {
            "query": query,
            "results": formatted_results,
            "total_found": len(semantic_results),
            "filters_applied": data_filters,
        }


    @server.tool(
        name="answer_general_question",
        description="Answer general questions about the user's data, schedule, or activities using semantic search",
        title="General Question Answering Tool",
    )
    async def answer_general_question(question: str) -> Dict[str, Any]:
        """
        Answer general questions about user's data, schedule, or activities.
        Automatically determines if semantic search is needed or if it's a simple question.
        
        Args:
            question: Natural language question from the user
            
        Returns:
            Dictionary with the answer and relevant information
        """
        logger.info(f"Answering general question: {question}")
        
        import re
        from datetime import datetime
        
        # Check if this is a simple date/time question
        date_time_keywords = ["what day", "what date", "today", "current date", "day of week", "now"]
        question_lower = question.lower()
        
        for keyword in date_time_keywords:
            if keyword in question_lower:
                # This is a simple date/time question, return current info
                today = datetime.now()
                return {
                    "answer": f"Today is {today.strftime('%A, %B %d, %Y')}",
                    "type": "date_info",
                    "timestamp": today.isoformat()
                }
        
        # For other questions, use semantic search
        semantic_results = rag_mcp_integrator.semantic_search(
            question, k=5, filters={}
        )
        
        # Format results
        formatted_results = []
        for result in semantic_results:
            formatted_results.append(
                {
                    "id": result["document"]["id"] if "document" in result else result.get("id", "unknown"),
                    "text": result["document"].get("text", result.get("text", "")) if "document" in result else result.get("text", ""),
                    "metadata": result["document"].get("metadata", result.get("metadata", {})) if "document" in result else result.get("metadata", {}),
                    "similarity_score": result.get("similarity_score", 0),
                    "source_type": result["document"].get("metadata", {}).get("type", "unknown") if "document" in result else result.get("source_type", "unknown"),
                }
            )
        
        return {
            "question": question,
            "results": formatted_results,
            "total_found": len(semantic_results),
            "type": "semantic_search",
            "answer": f"Found {len(semantic_results)} relevant results for your question: {question}"
        }

    @server.tool(
        name="get_location_nudge",
        description="Get contextual nudge based on current location and schedule",
        title="Location-Based Nudging Tool",
    )
    async def get_location_nudge(latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Generate contextual nudge based on user's current location and schedule.

        Args:
            latitude: Current latitude
            longitude: Current longitude

        Returns:
            Dictionary with location-based nudge suggestion and potential conflicts
        """
        logger.info(
            f"Generating location nudge for coordinates: ({latitude}, {longitude})"
        )

        # Use the location nudger to generate appropriate nudge
        nudge = location_nudger.generate_location_nudge(latitude, longitude)

        if nudge:
            return {
                "should_nudge": nudge["should_nudge"],
                "nudge_message": nudge["nudge_message"],
                "location_type": nudge["location_type"],
                "distance_to_location": nudge["distance"],
                "coordinates": (latitude, longitude),
                "conflicts": nudge["conflicts"],
                "actionable": True,
            }
        else:
            return {
                "should_nudge": False,
                "nudge_message": "No relevant nudges for your current location.",
                "location_type": "none",
                "distance_to_location": 999999,
                "coordinates": (latitude, longitude),
                "conflicts": [],
                "actionable": False,
            }

    @server.tool(
        name="analyze_behavioral_patterns",
        description="Analyze behavioral patterns from calendar, location, and fitness data",
        title="Behavioral Pattern Analysis Tool",
    )
    async def analyze_behavioral_patterns(
        time_period: str = "week", focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze behavioral patterns to identify trends, routines, and correlations.

        Args:
            time_period: Time period to analyze ('day', 'week', 'month', 'year')
            focus_areas: Specific areas to focus on (e.g., 'productivity', 'health', 'social')

        Returns:
            Dictionary with pattern analysis and insights
        """
        logger.info(
            f"Analyzing behavioral patterns for {time_period} period, focus: {focus_areas}"
        )

        # Map time period to number of days
        period_map = {"day": 1, "week": 7, "month": 30, "year": 365}
        days = period_map.get(time_period, 7)

        # Use the pattern analyzer to get insights
        patterns = pattern_analyzer.analyze_daily_patterns(days=days)

        # Filter based on focus areas if specified
        if focus_areas:
            filtered_patterns = {}
            for area in focus_areas:
                if area.lower() == "calendar":
                    filtered_patterns["calendar_analysis"] = patterns.get(
                        "calendar_analysis", {}
                    )
                elif area.lower() == "location":
                    filtered_patterns["location_analysis"] = patterns.get(
                        "location_analysis", {}
                    )
                elif area.lower() == "fitness":
                    filtered_patterns["fitness_analysis"] = patterns.get(
                        "fitness_analysis", {}
                    )
                elif area.lower() == "correlations":
                    filtered_patterns["cross_correlations"] = patterns.get(
                        "cross_correlations", {}
                    )
        else:
            filtered_patterns = patterns

        # Process with Hugging Face model to generate deeper insights
        prompt = f"""
        Analyze the following behavioral patterns for the {time_period} period:
        {filtered_patterns}
        
        Focus areas: {focus_areas or "all areas"}
        
        Provide insights about:
        1. Identified routines and habits
        2. Productivity patterns
        3. Health and wellness trends
        4. Social engagement patterns
        5. Correlations between different types of activities
        6. Recommendations for improvement
        """

        ai_analysis = _process_with_hf_model(prompt, enforce_quality=True)

        return {
            "patterns": filtered_patterns,
            "analysis": ai_analysis,
            "time_period": time_period,
            "focus_areas": focus_areas or ["all"],
        }

    @server.tool(
        name="generate_daily_summary",
        description="Generate a comprehensive daily summary with insights and analytics",
        title="Daily Summary Generator Tool",
    )
    async def generate_daily_summary(date: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive daily summary with insights and analytics.

        Args:
            date: Date to generate summary for (YYYY-MM-DD format, defaults to current date)

        Returns:
            Dictionary with daily summary and insights
        """
        logger.info(f"Generating daily summary for date: {date or 'today'}")

        # Use the daily summarizer to generate the summary
        summary = daily_summarizer.pattern_analyzer.generate_daily_summary(
            date=date or datetime.now().strftime("%Y-%m-%d")
        )

        # Process with Hugging Face model to enhance the summary
        prompt = f"""
        Generate a comprehensive daily summary for {summary["date"]}:
        
        Calendar Summary: {summary["calendar_summary"]}
        Location Summary: {summary["location_summary"]}
        Fitness Summary: {summary["fitness_summary"]}
        Day Rating: {summary["day_rating"]}/10
        Recommendations: {summary["recommendations"]}
        
        Create an engaging summary that highlights:
        1. Key accomplishments
        2. Notable patterns
        3. Areas for improvement
        4. Positive aspects of the day
        """

        enhanced_summary = _process_with_hf_model(prompt, enforce_quality=True)

        return {
            "date": summary["date"],
            "summary": enhanced_summary,
            "details": {
                "calendar": summary["calendar_summary"],
                "location": summary["location_summary"],
                "fitness": summary["fitness_summary"],
            },
            "rating": summary["day_rating"],
            "recommendations": summary["recommendations"],
        }

    @server.tool(
        name="generate_weekly_insights",
        description="Generate comprehensive weekly insights and trends",
        title="Weekly Insights Generator Tool",
    )
    async def generate_weekly_insights(
        start_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive weekly insights and trends.

        Args:
            start_date: Start date for the week (YYYY-MM-DD format, defaults to week start)

        Returns:
            Dictionary with weekly insights and analytics
        """
        logger.info(
            f"Generating weekly insights starting from: {start_date or 'current week start'}"
        )

        # Use the daily summarizer to generate weekly insights
        weekly_summary = daily_summarizer.generate_weekly_summary(
            start_date=start_date or datetime.now().strftime("%Y-%m-%d")
        )

        # Process with Hugging Face model to enhance insights
        prompt = f"""
        Generate comprehensive weekly insights for week starting {weekly_summary["week_starting"]}:
        
        Weekly Insights: {weekly_summary["weekly_insights"]}
        Daily Summaries: {list(weekly_summary["daily_summaries"].keys())[:3]}  # Show first 3 days
        Identified Trends: {weekly_summary["trends"]}
        Recommendations: {weekly_summary["recommendations"]}
        
        Create an engaging weekly summary that highlights:
        1. Major accomplishments and wins
        2. Identified patterns and trends
        3. Areas showing improvement
        4. Opportunities for enhancement
        5. Predictions for upcoming week
        """

        enhanced_insights = _process_with_hf_model(prompt, enforce_quality=True)

        return {
            "week_starting": weekly_summary["week_starting"],
            "insights": enhanced_insights,
            "detailed_summary": {
                "daily_summaries": weekly_summary["daily_summaries"],
                "weekly_insights": weekly_summary["weekly_insights"],
                "trends": weekly_summary["trends"],
            },
            "recommendations": weekly_summary["recommendations"],
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
            extensions = [
                ".py",
                ".js",
                ".ts",
                ".jsx",
                ".tsx",
                ".java",
                ".cpp",
                ".c",
                ".html",
                ".css",
                ".md",
            ]

        # Fetch code files from the project
        code_files = fetcher.fetch_files(extensions)

        # Filter and sort files based on relevance to the query
        filtered_files = []
        for file_info in code_files:
            # Look for the query term in filename or content
            if (
                query.lower() in file_info["filename"].lower()
                or query.lower() in file_info["content"].lower()
            ):
                filtered_files.append(file_info)

        # Sort by size and take top results
        filtered_files = sorted(filtered_files, key=lambda x: x["size"], reverse=True)[
            :max_results
        ]

        # Process the code content with Hugging Face model to generate analysis
        if filtered_files:
            code_context = "\n".join(
                [
                    f"File: {f['path']}\nContent Preview: {f['content'][:300]}...\n"
                    for f in filtered_files
                ]
            )
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
            all_files = sorted(code_files, key=lambda x: x["size"], reverse=True)[
                :max_results
            ]
            if all_files:
                code_context = "\n".join(
                    [
                        f"File: {f['path']}\nContent Preview: {f['content'][:200]}...\n"
                        for f in all_files
                    ]
                )
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

        ai_analysis = _process_with_hf_model(prompt, enforce_quality=True)

        # Prepare simplified file info for response
        result_files = []
        if filtered_files:  # Only process if filtered_files is not empty
            result_files = [
                {
                    "path": f["path"],
                    "filename": f["filename"],
                    "size": f["size"],
                    "lines": f["lines"],
                }
                for f in filtered_files
            ]

        return {
            "files": result_files,
            "analysis": ai_analysis,
            "count": len(result_files),
            "query": query,
        }

    @server.tool(
        name="analyze_codebase_patterns",
        description="Identify patterns in the codebase that may indicate optimization opportunities",
        title="Code Pattern Analysis Tool",
    )
    async def analyze_codebase_patterns() -> Dict[str, Any]:
        """
        Analyze the codebase to identify patterns that may indicate optimization opportunities.
        Looks for common patterns like repeated code, inefficient algorithms, etc.

        Returns:
            Analysis of codebase patterns with optimization suggestions
        """
        logger.info("Analyzing codebase patterns for optimization opportunities")

        # Import the codebase ingestion modules
        from data_ingestion.codebase.code_fetcher import CodeFetcher
        from data_ingestion.codebase.code_parser import analyze_codebase

        # Use the code fetcher and parser to analyze the codebase
        parsed_files = analyze_codebase()

        # Analyze patterns in the code
        pattern_analysis = {
            "total_files": len(parsed_files),
            "total_lines": sum(f.get("lines_of_code", 0) for f in parsed_files),
            "python_files": len([f for f in parsed_files if f["language"] == "python"]),
            "functions_count": sum(len(f["functions"]) for f in parsed_files),
            "classes_count": sum(len(f["classes"]) for f in parsed_files),
        }

        # Extract patterns found from each parsed file
        patterns_found = []
        for file_info in parsed_files:
            if "potential_issues" in file_info:
                for issue in file_info["potential_issues"]:
                    patterns_found.append(
                        {
                            "file": file_info["file_path"],
                            "pattern": issue,
                            "language": file_info["language"],
                        }
                    )

        # Process the pattern analysis with Hugging Face model to generate recommendations
        prompt = f"""
        Analyze the following codebase pattern analysis:
        Total files analyzed: {pattern_analysis["total_files"]}
        Total lines of code: {pattern_analysis["total_lines"]}
        Python files: {pattern_analysis["python_files"]}
        Total functions: {pattern_analysis["functions_count"]}
        Total classes: {pattern_analysis["classes_count"]}
        Patterns found that may indicate optimization opportunities:
        {[p["pattern"] + " in " + p["file"] for p in patterns_found[:10]]}  # Show first 10 patterns
        
        Provide specific recommendations for:
        1. Code structure improvements
        2. Performance optimizations
        3. Refactoring opportunities
        4. Best practices to implement
        """

        ai_recommendations = _process_with_hf_model(prompt, enforce_quality=True)

        return {
            "analysis": pattern_analysis,
            "patterns_found": patterns_found,
            "recommendations": ai_recommendations,
        }

    @server.tool(
        name="suggest_optimal_gym_time",
        description="Suggest optimal gym time based on calendar events and fitness patterns",
        title="Optimal Gym Time Suggestion Tool",
    )
    async def suggest_optimal_gym_time() -> Dict[str, Any]:
        """
        Suggest optimal gym time based on calendar events and fitness patterns.

        Returns:
            Dictionary with suggested gym times and reasoning
        """
        logger.info(
            "Generating optimal gym time suggestions based on calendar and fitness data"
        )

        # Load calendar events for today and the next few days
        import json
        import os
        from datetime import datetime, timedelta

        calendar_file = "data_sync/calendar_sync.json"
        calendar_events = []

        try:
            if os.path.exists(calendar_file):
                with open(calendar_file, "r") as f:
                    calendar_data = json.load(f)

                # Get events for today and next 2 days
                start_date = datetime.now()
                end_date = start_date + timedelta(days=2)

                for item in calendar_data:
                    metadata = item.get("metadata", {})
                    start_time = metadata.get("start_time", "")

                    if start_time:
                        try:
                            event_dt = datetime.fromisoformat(
                                start_time.replace("Z", "+00:00")
                            )
                            # Convert to naive datetime for comparison
                            event_dt = event_dt.replace(tzinfo=None)

                            if start_date <= event_dt <= end_date:
                                calendar_events.append(
                                    {
                                        "id": metadata.get("id", item.get("id", "")),
                                        "title": metadata.get(
                                            "summary", metadata.get("title", "No title")
                                        ),
                                        "start_time": metadata.get("start_time", ""),
                                        "end_time": metadata.get("end_time", ""),
                                        "location": metadata.get("location", ""),
                                        "attendees": metadata.get("attendees", []),
                                        "description": metadata.get("description", ""),
                                        "synced_at": metadata.get("synced_at", ""),
                                    }
                                )
                        except ValueError:
                            continue
        except Exception as e:
            logger.error(f"Error reading calendar data: {e}")

        # Load fitness data to understand patterns
        fitness_file = "data_sync/fit_sync.json"
        fitness_activities = []

        try:
            if os.path.exists(fitness_file):
                with open(fitness_file, "r") as f:
                    fitness_data = json.load(f)

                for item in fitness_data:
                    metadata = item.get("metadata", {})
                    timestamp = metadata.get("timestamp", "")

                    if timestamp:
                        try:
                            event_dt = datetime.fromisoformat(
                                timestamp.replace("Z", "+00:00")
                            )
                            # Convert to naive datetime for comparison
                            event_dt = event_dt.replace(tzinfo=None)

                            if start_date <= event_dt <= end_date:
                                fitness_activities.append(metadata)
                        except ValueError:
                            continue
        except Exception as e:
            logger.error(f"Error reading fitness data: {e}")

        # Find free time slots in the calendar
        free_slots = []
        day_start = datetime.combine(
            datetime.now().date(), datetime.min.time()
        ).replace(hour=6)  # Start at 6 AM
        day_end = datetime.combine(datetime.now().date(), datetime.min.time()).replace(
            hour=23
        )  # End at 11 PM

        # Sort events by start time
        sorted_events = sorted(calendar_events, key=lambda x: x["start_time"])

        current_time = day_start
        for event in sorted_events:
            event_start = datetime.fromisoformat(
                event["start_time"].replace("Z", "+00:00")
            ).replace(tzinfo=None)

            # Check if there's free time before this event
            if current_time < event_start:
                if (
                    event_start - current_time
                ).total_seconds() / 60 >= 30:  # At least 30 minutes free
                    free_slots.append(
                        {
                            "start": current_time.strftime("%H:%M"),
                            "end": event_start.strftime("%H:%M"),
                            "duration": int(
                                (event_start - current_time).total_seconds() / 60
                            ),
                        }
                    )

            # Update current time to end of this event
            try:
                event_end = datetime.fromisoformat(
                    event["end_time"].replace("Z", "+00:00")
                ).replace(tzinfo=None)
            except ValueError:
                event_end = event_start + timedelta(
                    hours=1
                )  # Default to 1-hour event if no end time

            current_time = max(current_time, event_end)

        # Add final free slot if any time remains until day_end
        if current_time < day_end:
            if (
                day_end - current_time
            ).total_seconds() / 60 >= 30:  # At least 30 minutes free
                free_slots.append(
                    {
                        "start": current_time.strftime("%H:%M"),
                        "end": day_end.strftime("%H:%M"),
                        "duration": int((day_end - current_time).total_seconds() / 60),
                    }
                )

        # Analyze fitness patterns to recommend optimal gym time
        preferred_times = []
        if fitness_activities:
            # Analyze when the user typically exercises
            morning_workouts = 0
            afternoon_workouts = 0
            evening_workouts = 0

            for activity in fitness_activities:
                time_of_day = datetime.fromisoformat(
                    activity["timestamp"].replace("Z", "+00:00")
                ).replace(tzinfo=None)
                hour = time_of_day.hour

                if 5 <= hour < 12:
                    morning_workouts += 1
                elif 12 <= hour < 18:
                    afternoon_workouts += 1
                else:
                    evening_workouts += 1

            # Create preference ranking based on historical data
            time_preferences = [
                ("morning", morning_workouts),
                ("afternoon", afternoon_workouts),
                ("evening", evening_workouts),
            ]
            time_preferences.sort(key=lambda x: x[1], reverse=True)

            for pref, count in time_preferences:
                if count > 0:
                    preferred_times.append(pref)

        # Generate gym time suggestions based on free slots and preferences
        suggestions = []
        for slot in free_slots:
            start_hour = int(slot["start"].split(":")[0])

            # Determine time of day
            if 5 <= start_hour < 12:
                time_of_day = "morning"
            elif 12 <= start_hour < 18:
                time_of_day = "afternoon"
            else:
                time_of_day = "evening"

            # Score the slot based on user preferences and duration
            score = 0
            if time_of_day in preferred_times:
                score += (
                    preferred_times.index(time_of_day) * 10
                )  # Higher preference gets higher score
            score += (
                min(slot["duration"] // 30, 4) * 5
            )  # Longer duration gets higher score (up to 2 hours)

            suggestions.append(
                {
                    "time_slot": f"{slot['start']} - {slot['end']}",
                    "duration_minutes": slot["duration"],
                    "time_of_day": time_of_day,
                    "score": score,
                    "suitability": "High"
                    if score >= 15
                    else "Medium"
                    if score >= 5
                    else "Low",
                }
            )

        # Sort suggestions by score (highest first)
        suggestions.sort(key=lambda x: x["score"], reverse=True)

        # Prepare response
        if suggestions:
            best_suggestion = suggestions[0]
            recommendation = f"Based on your calendar and fitness patterns, the best time for gym today is {best_suggestion['time_slot']} ({best_suggestion['time_of_day']}). Duration: {best_suggestion['duration_minutes']} minutes."
        else:
            # If no free slots, suggest early morning or late evening
            recommendation = "No extended free time found in your calendar today. Consider an early morning session (6-7 AM) or a late evening session (after 8 PM) if possible."

        # Also check for tomorrow if needed
        tomorrows_events = [
            event
            for event in calendar_events
            if datetime.fromisoformat(event["start_time"].replace("Z", "+00:00"))
            .replace(tzinfo=None)
            .date()
            == (datetime.now().date() + timedelta(days=1))
        ]

        tomorrow_suggestions = []  # Initialize the variable
        if not suggestions and tomorrows_events:
            # Find tomorrow's free slots
            tomorrow_free_slots = []
            tomorrow_start = datetime.combine(
                datetime.now().date() + timedelta(days=1), datetime.min.time()
            ).replace(hour=6)
            tomorrow_end = datetime.combine(
                datetime.now().date() + timedelta(days=1), datetime.min.time()
            ).replace(hour=23)

            tomorrows_sorted_events = sorted(
                tomorrows_events, key=lambda x: x["start_time"]
            )

            current_time = tomorrow_start
            for event in tomorrows_sorted_events:
                event_start = datetime.fromisoformat(
                    event["start_time"].replace("Z", "+00:00")
                ).replace(tzinfo=None)

                # Check if there's free time before this event
                if current_time < event_start:
                    if (
                        event_start - current_time
                    ).total_seconds() / 60 >= 30:  # At least 30 minutes free
                        tomorrow_free_slots.append(
                            {
                                "start": current_time.strftime("%H:%M"),
                                "end": event_start.strftime("%H:%M"),
                                "duration": int(
                                    (event_start - current_time).total_seconds() / 60
                                ),
                            }
                        )

                # Update current time to end of this event
                try:
                    event_end = datetime.fromisoformat(
                        event["end_time"].replace("Z", "+00:00")
                    ).replace(tzinfo=None)
                except ValueError:
                    event_end = event_start + timedelta(
                        hours=1
                    )  # Default to 1-hour event if no end time

                current_time = max(current_time, event_end)

            # Add final free slot if any time remains until tomorrow_end
            if current_time < tomorrow_end:
                if (
                    tomorrow_end - current_time
                ).total_seconds() / 60 >= 30:  # At least 30 minutes free
                    tomorrow_free_slots.append(
                        {
                            "start": current_time.strftime("%H:%M"),
                            "end": tomorrow_end.strftime("%H:%M"),
                            "duration": int(
                                (tomorrow_end - current_time).total_seconds() / 60
                            ),
                        }
                    )

            for slot in tomorrow_free_slots:
                start_hour = int(slot["start"].split(":")[0])

                # Determine time of day
                if 5 <= start_hour < 12:
                    time_of_day = "morning"
                elif 12 <= start_hour < 18:
                    time_of_day = "afternoon"
                else:
                    time_of_day = "evening"

                # Score the slot based on user preferences and duration
                score = 0
                if time_of_day in preferred_times:
                    score += preferred_times.index(time_of_day) * 10
                score += min(slot["duration"] // 30, 4) * 5

                tomorrow_suggestions.append(
                    {
                        "time_slot": f"{slot['start']} - {slot['end']}",
                        "duration_minutes": slot["duration"],
                        "time_of_day": time_of_day,
                        "score": score,
                        "suitability": "High"
                        if score >= 15
                        else "Medium"
                        if score >= 5
                        else "Low",
                    }
                )

            tomorrow_suggestions.sort(key=lambda x: x["score"], reverse=True)

            if tomorrow_suggestions:
                best_tomorrow = tomorrow_suggestions[0]
                recommendation += f" Tomorrow ({(datetime.now() + timedelta(days=1)).strftime('%A, %b %d')}) looks better: {best_tomorrow['time_slot']} ({best_tomorrow['time_of_day']}). Duration: {best_tomorrow['duration_minutes']} minutes."

        return {
            "recommendation": recommendation,
            "suggested_slots": suggestions[:3],  # Top 3 suggestions
            "tomorrow_suggestions": tomorrow_suggestions[:2],
            "free_time_slots": free_slots,
            "fitness_patterns": {
                "preferred_times": preferred_times,
                "recent_activities": len(fitness_activities),
            },
            "calendar_events_count": len(calendar_events),
            "data_considered": {
                "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "calendar_events": len(calendar_events),
                "fitness_activities": len(fitness_activities),
            },
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

        # Use semantic search to find events for the specific date
        query = f"calendar events on {date}"
        results = rag_mcp_integrator.semantic_search(
            query, k=10, filters={"type": "calendar_event"}
        )

        if results:
            events = []
            for result in results:
                metadata = result["document"]["metadata"]
                start_time = metadata.get("start_time", "Unknown time")
                title = metadata.get("summary", metadata.get("title", "Untitled"))
                events.append(
                    f"- {start_time.split('T')[1][:5] if 'T' in start_time else start_time}: {title}"
                )

            if events:
                return f"""
                Calendar for {date}:
                {"\n".join(events)}
                """
            else:
                return f"No events found for {date}. Day appears to be free."
        else:
            return f"""
            No calendar data available for {date}.
            This may indicate that calendar data hasn't been synced yet.
            """

    @server.resource("resource://habits/weekly-summary")
    async def get_weekly_habit_summary() -> str:
        """
        Get a summary of weekly habits and patterns.

        Returns:
            String representation of weekly habit summary
        """
        logger.info("Getting weekly habit summary")

        # Use semantic search to get recent fitness and location data for weekly summary
        query = "fitness activities and location visits from the last 7 days"
        results = rag_mcp_integrator.semantic_search(
            query, k=20, filters={"type": ["fitness_activity", "location"]}
        )

        # Categorize the results
        fitness_activities = [
            r
            for r in results
            if r["document"]["metadata"]["type"] == "fitness_activity"
        ]
        location_visits = [
            r for r in results if r["document"]["metadata"]["type"] == "location"
        ]

        if results:
            # Analyze the data to generate insights
            gym_visits = len(
                [
                    fa
                    for fa in fitness_activities
                    if "gym"
                    in str(fa["document"]["metadata"].get("activity_type", "")).lower()
                ]
            )
            walking_activities = len(
                [
                    fa
                    for fa in fitness_activities
                    if "walk"
                    in str(fa["document"]["metadata"].get("activity_type", "")).lower()
                ]
            )

            home_visits = len(
                [
                    lv
                    for lv in location_visits
                    if lv["document"]["metadata"].get("location_type") == "home"
                ]
            )
            work_visits = len(
                [
                    lv
                    for lv in location_visits
                    if lv["document"]["metadata"].get("location_type") == "work"
                ]
            )

            return f"""
            Weekly Habit Summary:
            Exercise: {gym_visits + walking_activities} activities (target: 5) - {min(100, int(((gym_visits + walking_activities) / 5) * 100))}% achievement
            Gym Sessions: {gym_visits} days
            Walking Activities: {walking_activities} sessions
            Home Visits: {home_visits} times
            Work Visits: {work_visits} times
            """
        else:
            return """
            No habit data available for the week.
            This may indicate that location and fitness data hasn't been synced yet.
            """

    @server.resource("resource://upcoming-events")
    async def get_upcoming_events() -> str:
        """
        Get upcoming calendar events.

        Returns:
            String representation of upcoming events
        """
        logger.info("Getting upcoming events")

        # Use semantic search to find upcoming events
        query = "upcoming calendar events"
        results = rag_mcp_integrator.semantic_search(
            query, k=10, filters={"type": "calendar_event"}
        )

        if results:
            events = []
            for result in results:
                metadata = result["document"]["metadata"]
                start_time = metadata.get("start_time", "Unknown time")
                title = metadata.get("summary", metadata.get("title", "Untitled"))

                # Format the event time nicely
                if "T" in start_time:
                    date_part = start_time.split("T")[0]
                    time_part = start_time.split("T")[1][:5]  # HH:MM format
                    events.append(f"- {date_part} {time_part}: {title}")
                else:
                    events.append(f"- {start_time}: {title}")

            if events:
                return f"""
                Upcoming Events:
                {"\n".join(events[:5])}  # Show first 5 events
                """
            else:
                return "No upcoming events found in your calendar."
        else:
            return """
            No upcoming events found.
            This may indicate that calendar data hasn't been synced yet.
            """


def _register_prompts(server: FastMCP):
    """Register prompts that guide the LLM on how to interact with NudgeAI."""

    @server.prompt(
        name="proactive-nudge",
        description="Generate a proactive nudge based on user's data and context using Hugging Face models with WhiteCircle quality validation",
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
        # Parse context for location information if available
        current_lat = None
        current_lng = None

        # Simple parsing to extract location from context if it contains coordinates
        if "latitude" in context.lower() and "longitude" in context.lower():
            try:
                # This assumes the context contains something like "latitude: X.XX, longitude: Y.YY"
                import re

                lat_match = re.search(
                    r"latitude[=:]\s*(-?\d+\.?\d*)", context, re.IGNORECASE
                )
                lng_match = re.search(
                    r"longitude[=:]\s*(-?\d+\.?\d*)", context, re.IGNORECASE
                )

                if lat_match and lng_match:
                    current_lat = float(lat_match.group(1))
                    current_lng = float(lng_match.group(1))
            except:
                pass  # If parsing fails, continue without location data

        # If we have location data, check for location-based nudges
        location_nudge = None
        if current_lat is not None and current_lng is not None:
            location_nudge = location_nudger.generate_location_nudge(
                current_lat, current_lng
            )

        # Get gym time suggestions if fitness goal is involved
        gym_suggestion = None
        if any(
            goal.lower() in ["fitness", "exercise", "workout", "gym", "training"]
            for goal in user_goals
        ):
            try:
                gym_suggestion = await suggest_optimal_gym_time()
            except:
                gym_suggestion = None  # If there's an error getting gym suggestions, continue without them

        # Build the prompt based on available information
        if location_nudge and location_nudge["should_nudge"]:
            # Include location-based nudge in the prompt
            if gym_suggestion:
                prompt = f"""
                Current context: {context}
                User goals: {", ".join(user_goals)}
                Location-based nudge: {location_nudge["nudge_message"]}
                Potential conflicts: {location_nudge["conflicts"]}
                Optimal gym time suggestion: {gym_suggestion["recommendation"]}
                
                Based on this information, provide a helpful, encouraging nudge that motivates the user toward their goals.
                Incorporate the location-based suggestion if appropriate and if there are no conflicts.
                Include the gym time recommendation if it's relevant to user goals.
                Be specific, actionable, and consider their current situation.
                Use a friendly, supportive tone that feels personal but professional.
                """
            else:
                prompt = f"""
                Current context: {context}
                User goals: {", ".join(user_goals)}
                Location-based nudge: {location_nudge["nudge_message"]}
                Potential conflicts: {location_nudge["conflicts"]}
                
                Based on this information, provide a helpful, encouraging nudge that motivates the user toward their goals.
                Incorporate the location-based suggestion if appropriate and if there are no conflicts.
                Be specific, actionable, and consider their current situation.
                Use a friendly, supportive tone that feels personal but professional.
                """
        else:
            if gym_suggestion:
                prompt = f"""
                Current context: {context}
                User goals: {", ".join(user_goals)}
                Optimal gym time suggestion: {gym_suggestion["recommendation"]}
                
                Based on this information, provide a helpful, encouraging nudge that motivates the user toward their goals.
                Include the gym time recommendation if it's relevant to user goals.
                Be specific, actionable, and consider their current situation.
                Use a friendly, supportive tone that feels personal but professional.
                """
            else:
                prompt = f"""
                Current context: {context}
                User goals: {", ".join(user_goals)}
                
                Based on this information, provide a helpful, encouraging nudge that motivates the user toward their goals.
                Be specific, actionable, and consider their current situation.
                Use a friendly, supportive tone that feels personal but professional.
                """

        # Generate the nudge with WhiteCircle quality enforcement
        ai_generated_nudge = _process_with_hf_model(prompt, enforce_quality=True)

        # Check if the response was flagged by WhiteCircle
        if (
            "WhiteCircle Quality Gate:" in ai_generated_nudge
            and "needs regeneration" in ai_generated_nudge
        ):
            # If flagged, create a special message indicating the need for regeneration
            return [
                {
                    "role": "system",
                    "content": "A quality check detected that the initial nudge may have contained hallucinations or low-quality content. The AI should now regenerate the nudge with strict adherence to factual accuracy and the provided context. Focus only on information that can be verified from the original context.",
                },
                {
                    "role": "user",
                    "content": f"Regenerate the nudge based on this context: {context} and goals: {', '.join(user_goals)}. Ensure all claims are factually accurate.",
                },
            ]
        else:
            return [
                {
                    "role": "system",
                    "content": "You are a proactive assistant that helps users achieve their goals by providing timely nudges based on their data and context. Consider location-based nudges when relevant.",
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
