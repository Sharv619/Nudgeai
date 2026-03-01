#!/bin/bash

# Script to start both the NudgeAI Simple API Server and the Frontend
echo "Starting NudgeAI Servers..."

# Function to start the Simple API Server
start_api_server() {
    echo "Starting Simple API Server on port 8001..."
    cd /home/lade/Hackathons/Mistral/Final/nudgeai
    source venv/bin/activate
    python simple_api_server.py &
    API_PID=$!
    echo "Simple API Server started with PID $API_PID"
}

# Function to start the Frontend
start_frontend() {
    echo "Starting Frontend on port 3000..."
    cd /home/lade/Hackathons/Mistral/Final/nudgeai/frontend
    npm run dev -- --host 0.0.0.0 &
    FRONTEND_PID=$!
    echo "Frontend started with PID $FRONTEND_PID"
}

# Start both servers
start_api_server
sleep 2  # Wait for API server to start
start_frontend

echo "Both servers are running:"
echo "- Simple API Server: http://localhost:8001"
echo "- Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes to finish
wait $API_PID $FRONTEND_PID