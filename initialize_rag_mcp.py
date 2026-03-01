#!/usr/bin/env python3
"""
Initialize the RAG-MCP integration by syncing data and indexing it into the vector database.
"""

import asyncio
import logging
from ragsystem.mcp_integration import rag_mcp_integrator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_rag_mcp_system():
    """
    Initialize the RAG-MCP system by syncing and indexing data.
    """
    logger.info("Initializing RAG-MCP integration system...")

    # Sync and index all available data
    logger.info("Syncing and indexing data into RAG system...")
    stats = rag_mcp_integrator.sync_and_index_all_data()

    logger.info(f"Data indexing completed with stats: {stats}")

    # Print final statistics
    rag_stats = rag_mcp_integrator.get_rag_stats()
    logger.info(f"Final RAG system stats: {rag_stats}")

    logger.info("RAG-MCP system initialized successfully!")

    # Test a sample semantic search to verify functionality
    logger.info("Testing semantic search functionality...")
    test_results = rag_mcp_integrator.semantic_search("recent calendar events", k=3)
    logger.info(f"Test search returned {len(test_results)} results")

    if test_results:
        logger.info("Sample result:")
        logger.info(f"  ID: {test_results[0]['document']['id']}")
        logger.info(
            f"  Text: {test_results[0]['document'].get('text', 'N/A')[:100]}..."
        )
        logger.info(f"  Similarity: {test_results[0]['similarity_score']:.3f}")

    return rag_stats


if __name__ == "__main__":
    initialize_rag_mcp_system()
