#!/usr/bin/env python3
"""
MCP API Bridge - Exposes NudgeAI MCP server tools as HTTP endpoints
This allows the frontend to call MCP tools and display real RAG-processed data
"""

import logging
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import your MCP server components
from ragsystem.mcp_integration import rag_mcp_integrator

# Import the MCP server tools directly
from mcp_server import create_nudgeai_mcp_server

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NudgeAI MCP API Bridge",
    description="HTTP bridge to expose NudgeAI MCP server tools",
    version="1.0.0",
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP server
try:
    mcp_server = create_nudgeai_mcp_server()
    logger.info("MCP server initialized successfully")

    # Note: The tools/resources will be accessible via the call_tool/read_resource methods
    # The MCP server is initialized and ready to handle requests
    logger.info("MCP server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MCP server: {e}")
    raise


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "NudgeAI MCP API Bridge",
        "version": "1.0.0",
        "description": "HTTP bridge to NudgeAI MCP server tools",
        "endpoints": {
            "calendar": "/api/calendar?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&event_type=optional",
            "location": "/api/location?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&location_type=optional",
            "habits": "/api/habits?time_period=week&focus_area=optional",
            "insights": "/api/insights?data_sources=calendar,location&focus_areas=productivity,health",
            "daily_summary": "/api/daily-summary?date=YYYY-MM-DD",
            "weekly_insights": "/api/weekly-insights?start_date=YYYY-MM-DD",
            "upcoming_events": "/api/upcoming-events",
            "location_nudge": "/api/location-nudge?latitude=XX.XX&longitude=YY.YY",
        },
    }


@app.get("/api/calendar")
async def api_query_calendar(
    start_date: str, end_date: str, event_type: Optional[str] = None
):
    """Query calendar events via MCP server"""
    try:
        # Call the MCP server tool directly using call_tool method
        result = await mcp_server.call_tool(
            "query_calendar",
            {"start_date": start_date, "end_date": end_date, "event_type": event_type},
        )

        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error querying calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/location")
async def api_query_location_history(
    start_date: str, end_date: str, location_type: Optional[str] = None
):
    """Query location history via MCP server"""
    try:
        result = await mcp_server.call_tool(
            "query_location_history",
            {
                "start_date": start_date,
                "end_date": end_date,
                "location_type": location_type,
            },
        )

        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error querying location history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/habits")
async def api_analyze_habits(
    time_period: str = Query("week", pattern="^(day|week|month)$"),
    focus_area: Optional[str] = None,
):
    """Analyze habits via MCP server"""
    try:
        result = await mcp_server.call_tool(
            "analyze_habits", {"time_period": time_period, "focus_area": focus_area}
        )

        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error analyzing habits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/insights")
async def api_get_personal_insights(
    data_sources: str = Query(..., description="Comma-separated list of data sources"),
    focus_areas: str = Query(..., description="Comma-separated list of focus areas"),
):
    """Get personal insights via MCP server"""
    try:
        # Parse comma-separated strings into lists
        sources_list = [source.strip() for source in data_sources.split(",")]
        areas_list = [area.strip() for area in focus_areas.split(",")]

        result = await mcp_server.call_tool(
            "get_personal_insights",
            {"data_sources": sources_list, "focus_areas": areas_list},
        )

        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting personal insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/daily-summary")
async def api_generate_daily_summary(date: Optional[str] = None):
    """Generate daily summary via MCP server"""
    try:
        result = await mcp_server.call_tool("generate_daily_summary", {"date": date})

        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error generating daily summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weekly-insights")
async def api_generate_weekly_insights(start_date: Optional[str] = None):
    """Generate weekly insights via MCP server"""
    try:
        result = await mcp_server.call_tool(
            "generate_weekly_insights", {"start_date": start_date}
        )

        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error generating weekly insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/upcoming-events")
async def api_get_upcoming_events():
    """Get upcoming events via MCP server resource"""
    try:
        # Call the resource using read_resource method
        result = await mcp_server.read_resource("resource://upcoming-events")

        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting upcoming events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/location-nudge")
async def api_get_location_nudge(latitude: float, longitude: float):
    """Get location-based nudge via MCP server"""
    try:
        result = await mcp_server.call_tool(
            "get_location_nudge", {"latitude": latitude, "longitude": longitude}
        )

        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting location nudge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/semantic-search")
async def api_semantic_search(
    query: str,
    data_filters: Optional[str] = None,
    max_results: int = Query(5, ge=1, le=20),
):
    """Perform semantic search across all data via MCP server"""
    try:
        # Parse comma-separated filters
        filters_list = None
        if data_filters:
            filters_list = [f.strip() for f in data_filters.split(",")]

        result = await mcp_server.call_tool(
            "semantic_search_all_data",
            {"query": query, "data_filters": filters_list, "max_results": max_results},
        )

        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error performing semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/ask-question")
async def api_answer_general_question(
    question: str,
):
    """Answer general questions using semantic search and RAG system"""
    try:
        result = await mcp_server.call_tool(
            "answer_general_question", {"question": question}
        )

        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rag-stats")
async def api_get_rag_stats():
    """Get RAG system statistics"""
    try:
        stats = rag_mcp_integrator.get_rag_stats()

        return {"success": True, "data": stats, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error getting RAG stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/test-connection")
async def api_test_connection():
    """Test connection to MCP server and RAG system"""
    try:
        # Test RAG system
        stats = rag_mcp_integrator.get_rag_stats()

        # Test a simple semantic search
        test_search = rag_mcp_integrator.semantic_search("test", k=1)

        return {
            "success": True,
            "message": "MCP server and RAG system are working",
            "rag_stats": stats,
            "test_search_results": len(test_search),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    # Run the API server
    print("🚀 Starting NudgeAI MCP API Bridge")
    print("API will be available at: http://localhost:8003")
    print("Frontend can connect at: http://localhost:8000/data_display.html")
    print("Press Ctrl+C to stop the server")

    uvicorn.run(
        "mcp_api_bridge:app", host="0.0.0.0", port=8003, reload=True, log_level="info"
    )
