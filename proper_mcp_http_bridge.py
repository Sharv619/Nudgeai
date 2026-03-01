#!/usr/bin/env python3
"""
Proper HTTP-to-MCP Bridge that follows MCP protocol standards
This creates a bridge between HTTP API and the MCP server using stdio communication
"""

import asyncio
import json
import logging
import subprocess
import sys
import threading
import queue
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import Future

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NudgeAI Proper MCP HTTP Bridge")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


import subprocess
from typing import Optional


class MCProtocolBridge:
    def __init__(self):
        self.mcp_process: Optional[subprocess.Popen] = None
        self.response_queues = {}  # Maps request IDs to queues for thread safety
        self.request_id_counter = 0
        self.lock = threading.Lock()
        self._start_mcp_server()

    def _start_mcp_server(self):
        """Start the MCP server as a subprocess"""
        try:
            # Start MCP server with stdio transport
            self.mcp_process = subprocess.Popen(
                [sys.executable, "mcp_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Start a daemon thread to read responses
            reader_thread = threading.Thread(target=self._read_responses, daemon=True)
            reader_thread.start()

            logger.info("MCP server started successfully")
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise

    def _read_responses(self):
        """Read responses from MCP server in a separate thread"""
        try:
            while True:
                if self.mcp_process.poll() is not None:
                    logger.error("MCP server process terminated")
                    break

                # Read line from stdout
                line = self.mcp_process.stdout.readline()

                if line.strip():
                    try:
                        response = json.loads(line.strip())
                        self._handle_response(response)
                    except json.JSONDecodeError as e:
                        logger.error(
                            f"Invalid JSON response: {line.strip()}, error: {e}"
                        )
        except Exception as e:
            logger.error(f"Error reading from MCP server: {e}")

    def _handle_response(self, response: Dict[str, Any]):
        """Handle an incoming response from the MCP server (thread-safe)"""
        with self.lock:
            request_id = response.get("id")
            if request_id in self.response_queues:
                # Put the response in the queue to signal completion
                response_queue = self.response_queues[request_id]
                response_queue.put(response)
                # Remove the entry to prevent memory leaks
                del self.response_queues[request_id]

    async def call_tool(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call an MCP tool via the protocol"""
        import queue
        import time

        # Create a queue to hold the response
        response_queue = queue.Queue()
        self.request_id_counter += 1
        request_id = self.request_id_counter

        # Register the queue (thread-safe)
        with self.lock:
            self.response_queues[request_id] = response_queue

        # Create the MCP request (JSON-RPC 2.0 format)
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }

        # Send request to MCP server
        request_json = json.dumps(request) + "\n"
        try:
            self.mcp_process.stdin.write(request_json)
            self.mcp_process.stdin.flush()
        except BrokenPipeError:
            raise HTTPException(status_code=500, detail="MCP server connection broken")

        # Wait for response with timeout (in a thread-safe way)
        try:
            # Poll for response with timeout
            timeout = 30.0
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Try to get response with a short timeout to avoid blocking
                    response = response_queue.get(timeout=0.1)
                    return response
                except queue.Empty:
                    # Check if the process is still alive
                    if self.mcp_process.poll() is not None:
                        raise HTTPException(
                            status_code=500, detail="MCP server process terminated"
                        )
                    continue

            # Timeout reached
            # Clean up by removing the queue from our registry
            with self.lock:
                if request_id in self.response_queues:
                    del self.response_queues[request_id]
            raise HTTPException(
                status_code=504, detail="Timeout waiting for MCP server response"
            )
        except Exception as e:
            # Clean up by removing the queue from our registry
            with self.lock:
                if request_id in self.response_queues:
                    del self.response_queues[request_id]
            raise HTTPException(
                status_code=500, detail=f"Error waiting for response: {str(e)}"
            )


# Global MCP bridge instance
mcp_bridge = MCProtocolBridge()


@app.on_event("startup")
async def startup_event():
    logger.info("Starting NudgeAI MCP HTTP Bridge")
    # MCP bridge is already initialized


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down NudgeAI MCP HTTP Bridge")
    if hasattr(mcp_bridge, "mcp_process") and mcp_bridge.mcp_process:
        mcp_bridge.mcp_process.terminate()
        mcp_bridge.mcp_process.wait()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if mcp_bridge.mcp_process and mcp_bridge.mcp_process.poll() is None:
        return {"status": "healthy", "mcp_server": "running"}
    else:
        return {"status": "unhealthy", "mcp_server": "not_running"}


# MCP Tool Endpoints - these follow the actual MCP protocol
@app.get("/api/mcp/tools/query_calendar")
async def get_calendar_events():
    """Call the query_calendar MCP tool"""
    from datetime import datetime, timedelta

    try:
        # Set default date range - next 7 days
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        params = {"start_date": start_date, "end_date": end_date}

        response = await mcp_bridge.call_tool("tools/query_calendar", params)
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        return response.get("result", {})
    except Exception as e:
        logger.error(f"Error calling query_calendar: {e}")
        raise HTTPException(status_code=500, detail=f"Calendar tool error: {str(e)}")


@app.get("/api/mcp/tools/query_drive")
async def search_documents(query: str = ""):
    """Call the query_drive_documents MCP tool"""
    try:
        params = {"query": query} if query else {}

        response = await mcp_bridge.call_tool("tools/query_drive_documents", params)
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        return response.get("result", {})
    except Exception as e:
        logger.error(f"Error calling query_drive_documents: {e}")
        raise HTTPException(status_code=500, detail=f"Document tool error: {str(e)}")


@app.get("/api/mcp/tools/query_location")
async def get_location_history():
    """Call the query_location_history MCP tool"""
    try:
        response = await mcp_bridge.call_tool("tools/query_location_history", {})
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        return response.get("result", {})
    except Exception as e:
        logger.error(f"Error calling query_location_history: {e}")
        raise HTTPException(status_code=500, detail=f"Location tool error: {str(e)}")


@app.get("/api/mcp/tools/query_fit")
async def get_health_data():
    """Call the semantic_search_all_data MCP tool for fitness data"""
    try:
        # Use the semantic search tool to query fitness-related data
        params = {
            "query": "fitness and health data",
            "data_filters": ["fitness", "health", "activity"],
            "max_results": 10,
        }
        response = await mcp_bridge.call_tool("tools/semantic_search_all_data", params)
        if "error" in response:
            # For debugging, log the error but try to return some data
            logger.warning(f"Semantic search returned error: {response['error']}")
            # Fallback to using query_codebase if semantic_search fails
            try:
                fallback_response = await mcp_bridge.call_tool(
                    "tools/query_codebase", {"query": "fitness data"}
                )
                if "error" not in fallback_response:
                    return fallback_response.get("result", {})
            except:
                pass
            raise HTTPException(status_code=500, detail=response["error"])
        return response.get("result", {})
    except Exception as e:
        logger.error(f"Error calling fitness-related tool: {e}")
        raise HTTPException(status_code=500, detail=f"Health tool error: {str(e)}")


@app.post("/api/mcp/tools/proactive-nudge")
async def get_proactive_nudge(request: Request):
    """Call the proactive-nudge MCP tool"""
    try:
        body = await request.json()
        response = await mcp_bridge.call_tool("tools/proactive-nudge", body)
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        return response.get("result", {})
    except Exception as e:
        logger.error(f"Error calling proactive-nudge: {e}")
        raise HTTPException(status_code=500, detail=f"Nudge tool error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
