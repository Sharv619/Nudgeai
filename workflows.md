# NudgeAI Workflows

This document outlines the core operational workflows within the NudgeAI system.

## 1. Data Ingestion & Synchronization
How NudgeAI keeps its knowledge base up-to-date.
1.  **Authentication**: OAuth 2.0 flow for Google Services (Calendar, Drive, Fit, Location).
2.  **Fetching**: Scheduled or manual execution of `fetch_*.py` scripts in `data_ingestion/`.
3.  **Normalization**: Raw API data is transformed into a consistent JSON format.
4.  **Indexing**: Data is processed through `ragsystem/embedding/` and stored in FAISS indices.
5.  **Sync Logging**: Tracking of synchronization status in `data_sync/`.

## 2. Universal Semantic Search Flow
How the system finds information across diverse data types.
1.  **Query Input**: User provides a natural language query via MCP tool or API.
2.  **Embedding**: Query is converted into a vector using Hugging Face models.
3.  **Vector Search**: RAG system performs similarity search against indexed data.
4.  **Filtering**: Results are optionally filtered by data type (e.g., only calendar, only documents).
5.  **Synthesis**: Results are combined and summarized using the LLM.

## 3. Proactive Nudging Workflow
How NudgeAI provides timely, context-aware suggestions.
1.  **Context Detection**: System receives current location (coordinates) and time.
2.  **Proximity Check**: `LocationNudger` determines if the user is near an "important location".
3.  **Calendar Scan**: System checks for immediate or upcoming schedule conflicts.
4.  **Nudge Generation**: If near a location and no conflicts exist, the LLM generates a personalized nudge.
5.  **Quality Check**: WhiteCircle validates the nudge for quality and factual accuracy.
6.  **Delivery**: Nudge is presented to the user.

## 4. Daily Summary Generation
How NudgeAI creates end-of-day reflections.
1.  **Data Aggregation**: `DailySummarizer` pulls all data points for the specified date.
2.  **Pattern Analysis**: `PatternAnalyzer` identifies trends and routines for that day.
3.  **Scoring**: System calculates a "Day Rating" based on activity levels and schedule adherence.
4.  **Insight Synthesis**: LLM creates a narrative summary with highlights and recommendations.
5.  **Persistence**: Summaries are stored for weekly trend analysis.

## 5. Codebase Analysis Workflow
How NudgeAI assists with software development.
1.  **Targeting**: `CodeFetcher` identifies source files in the project directory.
2.  **Parsing**: `CodeParser` analyzes file structure, functions, and classes.
3.  **Issue Detection**: System looks for patterns indicating optimization or refactoring opportunities.
4.  **Recommendation**: LLM provides specific code improvements and best practice suggestions.

## 6. MCP Tool Interaction
The standard flow for LLMs interacting with NudgeAI.
1.  **Tool Discovery**: LLM lists available tools via the MCP `list_tools` capability.
2.  **Tool Call**: LLM invokes a specific tool (e.g., `query_calendar`) with parameters.
3.  **Execution**: MCP Server processes the request, often involving the RAG system.
4.  **Response**: Server returns structured JSON data and optionally an AI-processed summary.
