# Hugging Face Integration with MCP Server for NudgeAI

This document explains how the Hugging Face integration works with the Model Context Protocol (MCP) server for NudgeAI.

## Overview

The NudgeAI MCP server integrates with Hugging Face models to provide enhanced processing capabilities for personal assistant tasks. This allows the server to leverage powerful language models for tasks such as:
- Analyzing calendar events and providing insights
- Processing location history for pattern recognition
- Searching and summarizing documents from Google Drive
- Generating personalized recommendations and nudges

## Architecture

```
[MCP-Compatible Client]
         |
         v
[Hugging Face MCP Server] <-- Uses Hugging Face models
         |
         v
[Data Sources: Calendar, Location, Drive]
```

## Key Components

### 1. Hugging Face Inference Client
- Uses your Hugging Face token from the `.env` file
- Connects to Hugging Face Hub to access models
- Currently configured for `mistralai/Mistral-7B-Instruct-v0.1`

### 2. MCP Tools with Hugging Face Enhancement
- `query_calendar`: Enhances calendar queries with AI insights
- `query_location_history`: Provides pattern analysis of location data
- `query_drive_documents`: Generates summaries of documents
- `analyze_habits`: Offers deep analysis of user habits
- `get_personal_insights`: Synthesizes insights across multiple data sources

### 3. Processing Flow
1. MCP client sends a request to the server
2. Server processes the request and gathers relevant data
3. Data is formatted into a prompt for the Hugging Face model
4. Hugging Face model generates enhanced insights
5. Server returns processed results to the client

## Configuration

### Environment Variables
Ensure your `.env` file contains:
```
HF_token=your_actual_hf_token_here
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.1  # Optional, defaults to this
```

### Changing the Model
To use a different Hugging Face model:
1. Update the `HF_MODEL` environment variable in your `.env` file
2. Restart the server

Example:
```
HF_MODEL=google/gemma-7b
```

## Usage

### Starting the Server
```bash
# Make sure you're in the project directory
cd /path/to/nudgeai

# Activate virtual environment
source venv/bin/activate

# Run the server
python mcp_server.py
```

Or use the convenience script:
```bash
./run_mcp_server.sh
```

### Connecting with MCP Clients
The server can be connected to by:
- Mistral Vibe
- Claude Desktop (with MCP support)
- Custom MCP clients
- Any other MCP-compatible applications

## Supported Models

The server works with any text generation model available on Hugging Face Hub. Popular choices include:
- Mistral models (e.g., `mistralai/Mistral-7B-Instruct-v0.1`)
- Llama models (if accessible)
- Gemma models (e.g., `google/gemma-7b`)
- Zephyr models (e.g., `HuggingFaceH4/zephyr-7b-beta`)

## Troubleshooting

### Common Issues

1. **Invalid Token Error**
   - Check that your Hugging Face token in `.env` is correct
   - Ensure the token has appropriate permissions for the model

2. **Model Access Error**
   - Verify the model name in `HF_MODEL` is correct
   - Check if the model requires additional access permissions

3. **Rate Limiting**
   - Some models have usage limits
   - Consider using open-weight models to avoid rate limits

### Verifying Setup
Run the test script to verify your setup:
```bash
python test_mcp_server.py
```

## Security Considerations

- Your Hugging Face token is loaded from the `.env` file and not hardcoded
- All communication follows the MCP specification for secure data exchange
- Data remains private as processing happens through the Hugging Face API
- No sensitive data is stored or logged by the server

## Performance Optimization

- The server caches frequently used data to reduce API calls
- Asynchronous processing ensures responsive performance
- Connection pooling optimizes API usage