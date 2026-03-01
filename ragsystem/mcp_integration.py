"""
Module to integrate RAG system with MCP tools for enhanced semantic search capabilities.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from ragsystem.indexing.vector_db import VectorDB
from ragsystem.embedding.generate import generate_embedding
from ragsystem.retrieval.search import RAGRetriever
from data_ingestion.data_sync_manager import DataSyncManager


logger = logging.getLogger(__name__)


class RAGMCPIntegrator:
    """
    Integrates the RAG system with MCP tools to provide enhanced semantic search capabilities.
    """

    def __init__(self):
        self.vector_db, self.retriever = self._initialize_rag_system()
        self.data_sync_manager = DataSyncManager()

    def _initialize_rag_system(self):
        """
        Initialize the RAG system components.
        """
        vector_db = VectorDB()
        retriever = RAGRetriever(vector_db)
        return vector_db, retriever

    def add_documents_to_rag(self, documents: List[Dict[str, Any]]) -> int:
        """
        Add documents to the RAG system for semantic search.
        """
        added_count = 0

        for doc in documents:
            try:
                # Generate embedding for the text
                embedding = generate_embedding(doc["text"])

                # Add to vector database
                self.vector_db.add_document(
                    doc_id=doc["id"], embedding=embedding, metadata=doc["metadata"]
                )

                added_count += 1

            except Exception as e:
                logger.error(f"Failed to add document {doc.get('id', 'unknown')}: {e}")

        return added_count

    def semantic_search(
        self, query: str, k: int = 5, filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search across all indexed data with optional filtering.
        """
        try:
            # Generate embedding for the query
            results = self.retriever.retrieve_relevant_documents(query, k=k)

            # Apply filters if provided
            if filters:
                filtered_results = []
                for result in results:
                    metadata = result["document"]["metadata"]

                    # Apply all filter criteria
                    match = True
                    for key, value in filters.items():
                        if key not in metadata:
                            match = False
                            break
                        if isinstance(value, list):
                            if metadata[key] not in value:
                                match = False
                                break
                        else:
                            if metadata[key] != value:
                                match = False
                                break

                    if match:
                        filtered_results.append(result)

                results = filtered_results[:k]

            return results

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    def find_similar_events(
        self, event_description: str, k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find events similar to the given description.
        """
        filters = {"type": "calendar_event"}
        return self.semantic_search(event_description, k=k, filters=filters)

    def location_pattern_search(
        self, location_type: str, time_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Search for location patterns within a specific time range.
        """
        # This would be a more sophisticated search in production
        query = f"location visits of type {location_type} in recent days"
        filters = {"location_type": location_type}
        results = self.semantic_search(query, k=10, filters=filters)

        # Filter by time range if needed
        if time_range:
            filtered_results = []
            for result in results:
                timestamp = result["document"]["metadata"].get("timestamp", "")
                if self._is_in_time_range(timestamp, time_range):
                    filtered_results.append(result)
            results = filtered_results

        return results

    def habit_similarity_search(
        self, habit_description: str, k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find habits or activities similar to the given description.
        """
        filters = {"type": ["fitness_activity", "location", "calendar_event"]}
        return self.semantic_search(habit_description, k=k, filters=filters)

    def _is_in_time_range(self, timestamp: str, time_range: Dict[str, str]) -> bool:
        """
        Check if a timestamp is within the specified time range.
        """
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            start_dt = datetime.fromisoformat(time_range["start"])
            end_dt = datetime.fromisoformat(time_range["end"])
            return start_dt <= dt <= end_dt
        except:
            return True  # If parsing fails, include by default

    def sync_and_index_all_data(self, data_types: List[str] = None) -> Dict[str, int]:
        """
        Perform data sync and add to RAG system automatically.
        """
        if data_types is None:
            data_types = [
                "calendar",
                "location",
                "fit",
            ]  # Exclude drive for now due to permissions

        # Create sync parameters
        sync_params = {
            "calendar": {"max_results": 15},
            "location": {"days": 14},
            "fit": {"days": 14},
        }

        # Perform sync
        sync_results = self.data_sync_manager.sync_all(sync_params)

        # Add each data type to RAG
        stats = {}
        for data_type in data_types:
            if data_type in sync_results:
                documents = sync_results[data_type]
                count = self.add_documents_to_rag(documents)
                stats[data_type] = count
                logger.info(f"Added {count} {data_type} documents to RAG")

        total_added = sum(stats.values())
        logger.info(f"Total: {total_added} documents added to RAG system")

        return stats

    def get_rag_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG database.
        """
        stats = {
            "document_count": self.vector_db.get_document_count(),
            "dimension": self.vector_db.dimension,
        }
        return stats


# Singleton instance for use in MCP tools
rag_mcp_integrator = RAGMCPIntegrator()
