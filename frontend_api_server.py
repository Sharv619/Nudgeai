#!/usr/bin/env python3
"""
HTTP API Server that acts as a bridge between the frontend and MCP server
This translates HTTP requests to MCP stdio protocol and back
"""

import asyncio
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import sys
import threading
import queue
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NudgeAI Frontend API Bridge")

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global reference to MCP server process
mcp_process = None
mcp_queue = queue.Queue()
response_waiters = {}


class MCPBridge:
    def __init__(self):
        # This bridge assumes that the MCP server is accessible via HTTP or other means
        # For now, we'll make it a simple placeholder that would connect to a running MCP server
        self.request_id_counter = 0
        logger.info("MCP Bridge initialized - expecting MCP server to be accessible")

    async def send_request(
        self, method: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Placeholder for sending a request to the MCP server"""
        # In a real implementation, this would connect to the running MCP server
        # For now, we'll just return an error if connection fails
        logger.warning(f"Attempting to send MCP request: {method}")
        try:
            # This would normally establish a connection to the running MCP server
            # For now, we'll just simulate the call by making a direct function call to the MCP server
            # But since MCP server runs via stdio, we'd need a different approach
            # This is a complex integration that would typically require either:
            # 1. Running the MCP server in TCP mode instead of stdio
            # 2. Having a separate HTTP wrapper around the MCP server
            # 3. Using shared memory or other IPC mechanism

            # For now, let's just return an error indicating the limitation
            raise HTTPException(
                status_code=500,
                detail="Direct MCP stdio communication not implemented in HTTP bridge. The MCP server needs to be accessible via HTTP or have a TCP adapter.",
            )
        except Exception as e:
            logger.error(f"Error sending request to MCP server: {e}")
            raise

    def _read_responses(self):
        """Read responses from MCP server in a separate thread"""
        try:
            while True:
                if self.process.poll() is not None:
                    logger.error("MCP server process terminated unexpectedly")
                    break

                # Read response from MCP server
                line = self.process.stdout.readline()
                if line:
                    try:
                        response = json.loads(line.decode("utf-8"))
                        # Handle the response based on its type
                        self._handle_response(response)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON response from MCP: {line}")
                    except Exception as e:
                        logger.error(f"Error processing MCP response: {e}")
        except Exception as e:
            logger.error(f"Error reading from MCP server: {e}")

    def _handle_response(self, response: Dict[str, Any]):
        """Handle response from MCP server"""
        # If this is a response to a specific request, notify the waiter
        request_id = response.get("id")
        if request_id in self.response_callbacks:
            callback = self.response_callbacks.pop(request_id)
            callback(response)

    async def send_request(
        self, method: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Send a request to the MCP server and wait for response"""
        # Create a request ID
        self.request_id_counter += 1
        req_id = self.request_id_counter

        # Create MCP request
        request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {},
        }

        # Store callback for response
        response_future = asyncio.Future()
        self.response_callbacks[req_id] = lambda resp: response_future.set_result(resp)

        # Send request to MCP server
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode("utf-8"))
        self.process.stdin.flush()

        # Wait for response with timeout
        try:
            response = await asyncio.wait_for(response_future, timeout=30.0)
            return response
        except asyncio.TimeoutError:
            # Remove callback if timed out
            self.response_callbacks.pop(req_id, None)
            raise HTTPException(
                status_code=504, detail="Timeout waiting for MCP server response"
            )


# Global MCP bridge instance
mcp_bridge = MCPBridge()


@app.on_event("startup")
async def startup_event():
    logger.info("Starting NudgeAI Frontend API Bridge")
    # MCP bridge is already initialized globally


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down NudgeAI Frontend API Bridge")
    if mcp_bridge.process:
        mcp_bridge.process.terminate()
        mcp_bridge.process.wait()


# API endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if mcp_process and mcp_process.poll() is None:
        return {"status": "healthy", "mcp_server": "running"}
    else:
        return {"status": "unhealthy", "mcp_server": "not_running"}


@app.get("/api/mcp/tools")
async def get_available_tools():
    """Get available MCP tools"""
    try:
        # This would need to query the MCP server for available tools
        # For now, return a basic response
        response = await mcp_bridge.send_request("mcp/listTools", {})
        return response
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        raise HTTPException(status_code=500, detail=f"MCP server error: {str(e)}")


@app.post("/api/mcp/tools/{tool_name}")
async def execute_tool(tool_name: str, request: Request):
    """Execute an MCP tool"""
    try:
        body = await request.json()
        # Map frontend tool names to MCP tool names
        mcp_tool_mapping = {
            "query_calendar": "query_calendar",
            "query_drive": "query_drive_documents",
            "query_location": "query_location_history",
            "query_fit": "semantic_search_all_data",  # Fitness data accessed through semantic search
            "proactive-nudge": "proactive-nudge",
        }

        mcp_tool_name = mcp_tool_mapping.get(tool_name, tool_name)
        response = await mcp_bridge.send_request(f"tools/{mcp_tool_name}", body)
        return response
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Tool execution error: {str(e)}")


@app.get("/api/mcp/tools/query_calendar")
async def get_calendar_events():
    """Get calendar events"""
    try:
        response = await mcp_bridge.send_request("tools/query-calendar", {})
        return response
    except Exception as e:
        logger.error(f"Error getting calendar events: {e}")
        raise HTTPException(status_code=500, detail=f"Calendar error: {str(e)}")


@app.get("/api/mcp/tools/query_drive")
async def search_documents(query: str = ""):
    """Search documents"""
    try:
        # Pass the query as a parameter in the expected format
        params = {"query": query} if query else {}
        response = await mcp_bridge.send_request("tools/query_drive_documents", params)
        return response
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=f"Document search error: {str(e)}")


@app.get("/api/mcp/tools/query_location")
async def get_location_history():
    """Get location history"""
    try:
        response = await mcp_bridge.send_request("tools/query-location", {})
        return response
    except Exception as e:
        logger.error(f"Error getting location history: {e}")
        raise HTTPException(status_code=500, detail=f"Location error: {str(e)}")


@app.get("/api/mcp/tools/query_fit")
async def get_health_data():
    """Get health/fitness data"""
    try:
        response = await mcp_bridge.send_request("tools/query-fit", {})
        return response
    except Exception as e:
        logger.error(f"Error getting health data: {e}")
        raise HTTPException(status_code=500, detail=f"Health data error: {str(e)}")


@app.post("/api/mcp/tools/proactive-nudge")
async def get_proactive_nudge(request: Request):
    """Get proactive nudge"""
    try:
        body = await request.json()
        response = await mcp_bridge.send_request("tools/proactive-nudge", body)
        return response
    except Exception as e:
        logger.error(f"Error getting proactive nudge: {e}")
        raise HTTPException(status_code=500, detail=f"Nudge error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
