# Codebase Analysis Extension Plan

## Objective
Extend the NudgeAI MCP server to analyze the local codebase and provide optimization suggestions using the existing MCP tool framework.

## Current MCP Tool Architecture
The existing MCP server provides tools for:
- `query_calendar`: Calendar events with AI analysis
- `query_location_history`: Location patterns with AI processing
- `query_drive_documents`: Drive document search with AI summaries
- `analyze_habits`: Habit analysis using Hugging Face models
- `get_personal_insights`: Comprehensive insights from multiple data sources

## Extension Plan

### 1. New Data Ingestion Module: Codebase Ingestion
Create `data_ingestion/codebase/` with:
- `code_fetcher.py`: Fetches code files from the local project
- `code_parser.py`: Parses code files and extracts relevant information
- `code_chunker.py`: Chunks code into digestible segments for analysis

### 2. Extend MCP Tools
Add new tools to the MCP server:
- `query_codebase`: Search through codebase files with AI analysis
- `analyze_codebase_patterns`: Identify patterns in the codebase that may indicate optimization opportunities
- `suggest_optimizations`: Provide specific optimization suggestions based on code analysis

### 3. Implementation Strategy
- Leverage existing embedding and processing infrastructure
- Adapt the existing tool structure to work with code files
- Use the same Hugging Face integration for AI-powered analysis
- Store code embeddings in ChromaDB for retrieval

### 4. File Structure
```
data_ingestion/
├── calendar/
├── drive/
├── location/
└── codebase/                 # New module
    ├── code_fetcher.py       # Fetch code files
    ├── code_parser.py        # Parse code files
    └── code_chunker.py       # Chunk code for processing

ragsystem/
├── embedding/
├── indexing/
└── retrieval/

llm/
```

This extension builds on the existing architecture while adding codebase analysis capabilities.