# NudgeAI Developer Guidelines

## Project Overview
NudgeAI is a personal productivity assistant using MCP (Model Context Protocol) with Google API integrations, RAG (Retrieval-Augmented Generation), and WhiteCircle quality validation.

## Build/Lint/Test Commands

### Setup & Installation
```bash
# Install core dependencies
pip install -r requirements.txt

# Install MCP-specific dependencies
pip install -r mcp_requirements.txt

# Load environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Building & Running
```bash
# Start MCP server
python mcp_server.py

# Alternative: Use the startup script
./run_mcp_server.sh

# Start HTTP API bridge (recommended for frontend integration)
python simple_api_server.py

# Run data ingestion
python -m data_ingestion.calendar.fetch_calendar_events
python -m data_ingestion.drive.fetch_drive_documents
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_specific.py

# Run single test function
python -m pytest tests/test_file.py::test_function_name -v

# Run integration tests
python test_rag_integration.py
python test_full_integration.py
python test_rag_mcp_integration.py

# Test MCP connectivity
python test_mcp_server.py

# Run individual test files directly
python test_codebase_analysis.py
python test_whitecircle_integration.py
python test_phase2_implementation.py
python test_phase2_complete.py

# For debugging tests with verbose output
python -m pytest tests/ -v -s
```

### Linting & Code Quality
```bash
# Python linting
ruff check .
ruff format .
black .

# Type checking
mypy .

# Security scanning
bandit -r .
```

### Building & Running
```bash
# Start MCP server
python mcp_server.py

# Alternative: Use the startup script
./run_mcp_server.sh

# Run data ingestion
python -m data_ingestion.calendar.fetch_calendar_events
python -m data_ingestion.drive.fetch_drive_documents
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_specific.py

# Run single test function
python -m pytest tests/test_file.py::test_function_name -v

# Run integration tests
python test_rag_integration.py
python test_full_integration.py

# Test MCP connectivity
python test_mcp_server.py
```

### Linting & Code Quality
```bash
# Python linting
ruff check .
ruff format .
black .

# Type checking
mypy .

# Security scanning
bandit -r .
```

## Code Style Guidelines

### Imports
- Group imports in order: standard library, third-party, first-party
- Use absolute imports over relative imports
- Avoid wildcard imports (`from module import *`)
- Import specific functions/classes rather than entire modules when possible

```python
# Standard library
import os
import json
from datetime import datetime

# Third-party
import requests
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP

# First-party
from ragsystem.embedding.generate import generate_embedding
from data_ingestion.calendar.fetch_calendar_events import fetch_events
```

### Formatting
- Line length: 88-100 characters
- Use double quotes for strings, single quotes for docstrings
- Use f-strings for string formatting
- Follow PEP 8 style guide
- Use consistent indentation (4 spaces)

### Type Hints
- Use type hints for all function signatures
- Use `from __future__ import annotations` for forward references
- Use `Union[str, int]` or `str | int` (Python 3.10+) for union types
- Use `Optional[T]` or `T | None` for optional values

```python
from typing import List, Dict, Optional, Any
from datetime import datetime

def process_events(events: List[Dict[str, Any]], 
                 max_results: Optional[int] = None) -> List[str]:
    ...
```

### Naming Conventions
- Use snake_case for functions, variables, and modules
- Use PascalCase for classes
- Use UPPER_CASE for constants
- Prefix private methods/attributes with underscore
- Use descriptive names (avoid abbreviations like `lst`, `dct`)

### Error Handling
- Use specific exception types rather than generic `Exception`
- Include meaningful error messages
- Use try-except blocks appropriately
- Log errors with context using the logging module
- Fail gracefully with fallback mechanisms

```python
import logging

logger = logging.getLogger(__name__)

def fetch_data(url: str) -> dict:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from {url}: {e}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response from {url}: {e}")
        return {}
```

### Documentation
- Use Google-style docstrings for functions and classes
- Document parameters, return values, and exceptions
- Include examples when beneficial
- Keep docstrings up to date with code changes

```python
def calculate_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector for comparison
        vec2: Second vector for comparison
        
    Returns:
        Cosine similarity score between -1 and 1
        
    Raises:
        ValueError: If vectors have different dimensions
    """
    ...
```

### Security Practices
- Never commit API keys or credentials to the repository
- Use environment variables for sensitive data
- Validate and sanitize all inputs
- Use HTTPS for external API calls
- Implement proper authentication flows

### MCP Protocol Compliance
- Follow MCP (Model Context Protocol) specifications
- Use proper typing for MCP responses
- Handle streaming responses correctly
- Implement proper resource management
- Follow MCP error handling conventions
- Maintain compatibility with MCP tool definitions
- Include proper error responses with codes and messages

### Google API Integration
- Implement proper OAuth 2.0 flows
- Handle token refresh automatically
- Respect API quotas and rate limits
- Use appropriate scopes for data access
- Implement fallback mechanisms for API errors
- Cache API responses to reduce quota usage

### RAG System Standards
- Maintain consistent embedding dimensions (384 for all-MiniLM-L6-v2)
- Implement proper metadata preservation
- Follow FAISS best practices for indexing
- Include proper error handling for vector operations
- Maintain data consistency across ingestion sources

### WhiteCircle Integration
- Validate all responses through WhiteCircle quality gates
- Implement retry mechanisms for failed validations
- Log validation results for monitoring
- Maintain response quality standards

### Data Integration Patterns
- Always provide fallback data when primary sources unavailable
- Implement proper error boundaries for data fetching
- Use consistent data structures across all data sources
- Include timestamps and metadata with all data
- Implement proper data caching strategies
- Handle different data formats (JSON, CSV, etc.) consistently

## File Structure
- `mcp_server.py`: Main MCP server implementation
- `data_ingestion/`: Google API data fetching modules
- `ragsystem/`: RAG components (embedding, indexing, retrieval)
- `tests/`: Unit and integration tests
- `docs/`: Documentation files
- `api/`: API endpoints (if applicable)
- `cli/`: Command-line interface tools
- `config/`: Configuration files

## Best Practices
- Write comprehensive unit tests for new functionality
- Use meaningful commit messages following conventional commits
- Keep functions focused with single responsibility
- Implement logging for debugging and monitoring
- Handle edge cases and error conditions gracefully
- Write maintainable, readable code over clever solutions