#!/usr/bin/env python3
"""
Simple MCP HTTP Gateway - connects HTTP requests to MCP server via stdio
"""

import json
import logging
import subprocess
import sys
import threading
import time
from queue import Queue, Empty
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NudgeAI MCP HTTP Gateway")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimpleMCPBridge:
    def __init__(self):
        self.process = None
        self.response_queues = {}  # Maps request IDs to response queues
        self.request_id_counter = 0
        self.lock = threading.Lock()
        self.running = False
        self.reader_thread = None
        self._start_mcp_server()

    def _start_mcp_server(self):
        """Start the MCP server subprocess"""
        try:
            self.process = subprocess.Popen(
                [sys.executable, "mcp_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            self.running = True

            # Start reader thread
            self.reader_thread = threading.Thread(
                target=self._read_responses, daemon=True
            )
            self.reader_thread.start()

            logger.info("MCP server started successfully")
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise

    def _read_responses(self):
        """Read responses from MCP server in a separate thread"""
        try:
            while self.running:
                if self.process.poll() is not None:
                    logger.error("MCP server process terminated")
                    self.running = False
                    break

                try:
                    # Read a line from stdout with timeout
                    line = self.process.stdout.readline()
                    if line:
                        line = line.strip()
                        if line:
                            response = json.loads(line)
                            self._handle_response(response)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON response: {line}, error: {e}")
                except Exception as e:
                    logger.error(f"Error reading response: {e}")
                    time.sleep(0.1)  # Brief pause to prevent busy-waiting
        except Exception as e:
            logger.error(f"Reader thread error: {e}")
        finally:
            self.running = False

    def _handle_response(self, response: Dict[str, Any]):
        """Handle incoming response from MCP server"""
        req_id = response.get("id")
        if req_id is not None and req_id in self.response_queues:
            with self.lock:
                queue = self.response_queues[req_id]
            # Put the response in the queue to unblock the waiting request
            queue.put(response)
            # Remove from tracking to prevent memory leak
            with self.lock:
                if req_id in self.response_queues:
                    del self.response_queues[req_id]

    def call_mcp_method(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """Synchronously call an MCP method"""
        if not self.running or (self.process and self.process.poll() is not None):
            raise HTTPException(status_code=500, detail="MCP server is not running")

        # Create a queue to receive the response
        response_queue = Queue()

        # Generate request ID and register the queue
        with self.lock:
            self.request_id_counter += 1
            req_id = self.request_id_counter
            self.response_queues[req_id] = response_queue

        # Create the MCP request
        request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {},
        }

        # Send request to MCP server
        request_str = json.dumps(request) + "\n"
        try:
            self.process.stdin.write(request_str)
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            logger.error(f"Failed to send request to MCP server: {e}")
            with self.lock:
                if req_id in self.response_queues:
                    del self.response_queues[req_id]
            raise HTTPException(
                status_code=500, detail="Failed to communicate with MCP server"
            )

        # Wait for response
        try:
            # Wait for response with timeout
            response = response_queue.get(timeout=timeout)
            return response
        except Empty:
            # Timeout occurred
            with self.lock:
                if req_id in self.response_queues:
                    del self.response_queues[req_id]
            raise HTTPException(
                status_code=504, detail="Timeout waiting for MCP server response"
            )


# Global MCP bridge instance
mcp_bridge = SimpleMCPBridge()


@app.on_event("startup")
async def startup_event():
    logger.info("Starting NudgeAI MCP HTTP Gateway")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down NudgeAI MCP HTTP Gateway")
    mcp_bridge.running = False
    if mcp_bridge.process:
        mcp_bridge.process.terminate()
        mcp_bridge.process.wait(timeout=5)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    is_running = (
        mcp_bridge.running and mcp_bridge.process and mcp_bridge.process.poll() is None
    )
    return {
        "status": "healthy" if is_running else "unhealthy",
        "mcp_server": "running" if is_running else "not_running",
    }


# MCP Tool Endpoints
@app.get("/api/mcp/tools/query_calendar")
async def get_calendar_events():
    """Query calendar events using MCP protocol"""
    try:
        # Use the next 7 days as default range
        from datetime import datetime, timedelta

        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        params = {"start_date": start_date, "end_date": end_date}

        response = mcp_bridge.call_mcp_method("tools/query_calendar", params)

        if "error" in response:
            logger.error(f"MCP error: {response['error']}")
            raise HTTPException(
                status_code=500, detail=f"MCP Error: {response['error']}"
            )

        return response.get("result", {})
    except Exception as e:
        logger.error(f"Error in query_calendar: {e}")
        raise


@app.get("/api/mcp/tools/query_drive")
async def search_documents(query: str = ""):
    """Search documents using MCP protocol"""
    try:
        params = {"query": query} if query else {}
        response = mcp_bridge.call_mcp_method("tools/query_drive_documents", params)

        if "error" in response:
            logger.error(f"MCP error: {response['error']}")
            raise HTTPException(
                status_code=500, detail=f"MCP Error: {response['error']}"
            )

        return response.get("result", {})
    except Exception as e:
        logger.error(f"Error in query_drive_documents: {e}")
        raise


@app.get("/api/mcp/tools/query_location")
async def get_location_history():
    """Get location history using MCP protocol"""
    try:
        # Use recent week as default
        from datetime import datetime, timedelta

        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        params = {"start_date": start_date, "end_date": end_date}

        response = mcp_bridge.call_mcp_method("tools/query_location_history", params)

        if "error" in response:
            logger.error(f"MCP error: {response['error']}")
            raise HTTPException(
                status_code=500, detail=f"MCP Error: {response['error']}"
            )

        return response.get("result", {})
    except Exception as e:
        logger.error(f"Error in query_location_history: {e}")
        raise


@app.get("/api/mcp/tools/query_fit")
async def get_health_data():
    """Get health data using MCP protocol"""
    try:
        # Use semantic search for fitness data
        params = {
            "query": "fitness and health activities",
            "data_filters": ["fitness", "health"],
            "max_results": 10,
        }

        response = mcp_bridge.call_mcp_method("tools/semantic_search_all_data", params)

        if "error" in response:
            logger.error(f"MCP error: {response['error']}")
            raise HTTPException(
                status_code=500, detail=f"MCP Error: {response['error']}"
            )

        return response.get("result", {})
    except Exception as e:
        logger.error(f"Error in health data query: {e}")
        raise


@app.post("/api/mcp/tools/proactive-nudge")
async def get_proactive_nudge(request: Request):
    """Get proactive nudge using MCP protocol"""
    try:
        body = await request.json()
        # Default to a general nudge if no context provided
        if not body:
            body = {"context": "general_recommendations"}

        response = mcp_bridge.call_mcp_method("tools/proactive-nudge", body)

        if "error" in response:
            logger.error(f"MCP error: {response['error']}")
            raise HTTPException(
                status_code=500, detail=f"MCP Error: {response['error']}"
            )

        return response.get("result", {})
    except Exception as e:
        logger.error(f"Error in proactive-nudge: {e}")
        raise


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
