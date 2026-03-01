# NudgeAI MCP Server with Hugging Face Integration

This MCP (Model Context Protocol) server integrates your NudgeAI personal assistant with Hugging Face models for enhanced processing and AI capabilities.

## Setup

### Prerequisites
- Python 3.8+
- Hugging Face access token (already configured in your `.env` file)

### Installation

1. Install the required dependencies:
   ```bash
   pip install -r mcp_requirements.txt
   ```

2. Ensure your Hugging Face token is properly configured in the `.env` file:
   ```
   HF_token=your_actual_hf_token_here
   ```

3. Install the main project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

1. Start the MCP server:
   ```bash
   python mcp_server.py
   ```

2. The server will start and listen for MCP-compatible clients.

## Features

### Tools
- `query_calendar`: Query calendar events and get AI-analyzed insights
- `query_location_history`: Analyze location patterns with Hugging Face processing
- `query_drive_documents`: Search Drive documents with AI-generated summaries
- `analyze_habits`: Deep habit analysis using Hugging Face models
- `get_personal_insights`: Comprehensive insights from multiple data sources

### Resources
- Daily calendar availability
- Weekly habit summaries
- Upcoming events

### Prompts
- Proactive nudge generation using Hugging Face models

## Integration with Hugging Face

The server uses your Hugging Face token to:
- Access models from the Hugging Face Hub
- Process data with powerful language models
- Generate personalized insights and recommendations

Currently configured to use: `mistralai/Mistral-7B-Instruct-v0.1` (can be changed in the `.env` file)

## Usage with MCP-compatible Clients

Once running, the server can be connected to by:
- Mistral Vibe
- Claude Desktop (with MCP support)
- Custom MCP clients
- Any other MCP-compatible applications

## Testing

To test the server setup:
```bash
python test_mcp_server.py
```

## Security

- Your Hugging Face token is loaded from the `.env` file and not hardcoded
- All communication follows the MCP specification for secure data exchange
- Data remains private as processing happens locally

## Troubleshooting

If you encounter issues:
1. Verify your Hugging Face token is valid
2. Check that the model name in `.env` is accessible
3. Ensure all dependencies are installed
4. Look at the server logs for error messages