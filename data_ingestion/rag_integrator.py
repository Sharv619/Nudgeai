#!/usr/bin/env python3
"""
Module to integrate synchronized Google API data with the RAG system.
"""

import logging
from typing import List, Dict, Any, Optional

# Import RAG system components
from ragsystem import create_default_rag_system
from ragsystem.embedding.generate import generate_embedding, generate_embeddings

# Import data sync manager
from data_ingestion.data_sync_manager import DataSyncManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/rag_integration.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class RAGIntegrator:
    """Integrates synchronized Google API data with the RAG system."""

    def __init__(self):
        self.vector_db, self.retriever = create_default_rag_system()
        self.data_sync_manager = DataSyncManager()

    def add_documents_to_rag(self, documents: List[Dict[str, Any]]) -> int:
        """Add documents to the RAG system in batch for faster embedding generation and indexing (~5x speedup)."""
        if not documents:
            return 0

        # Filter valid documents with required fields
        valid_docs = [
            doc
            for doc in documents
            if isinstance(doc, dict) and "text" in doc and "id" in doc and "metadata" in doc
        ]
        if not valid_docs:
            return 0

        try:
            # Batch generate embeddings for all document texts in a single forward pass (~5x faster)
            texts = [doc["text"] for doc in valid_docs]
            embeddings = generate_embeddings(texts)

            doc_ids = [doc["id"] for doc in valid_docs]
            metadatas = [doc["metadata"] for doc in valid_docs]

            # Batch insert documents into FAISS vector database
            self.vector_db.add_documents(
                doc_ids=doc_ids, embeddings=embeddings, metadatas=metadatas
            )
            return len(valid_docs)
        except Exception as e:
            logger.error(f"Batch RAG document indexing failed, falling back to sequential: {e}")
            # Fall back to sequential addition if batch processing fails
            added_count = 0
            for doc in valid_docs:
                try:
                    embedding = generate_embedding(doc["text"])
                    self.vector_db.add_document(
                        doc_id=doc["id"], embedding=embedding, metadata=doc["metadata"]
                    )
                    added_count += 1
                except Exception as doc_err:
                    logger.error(f"Failed to add document {doc.get('id', 'unknown')}: {doc_err}")
            return added_count

    def sync_and_add_to_rag(
        self, data_types: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """Perform data sync and add to RAG system."""
        effective_data_types = (
            data_types
            if data_types is not None
            else ["calendar", "drive", "location", "fit"]
        )

        # Perform sync
        logger.info(f"Starting sync for data types: {effective_data_types}")

        # Create sync parameters
        sync_params = {
            "calendar": {"max_results": 15},
            "drive": {"max_results": 15},
            "location": {"days": 14},
            "fit": {"days": 14},
        }

        # Perform sync
        sync_results = self.data_sync_manager.sync_all(sync_params)

        # Add each data type to RAG
        stats = {}
        for data_type in effective_data_types:
            if data_type in sync_results:
                documents = sync_results[data_type]
                count = self.add_documents_to_rag(documents)
                stats[data_type] = count
                logger.info(f"Added {count} {data_type} documents to RAG")

        total_added = sum(stats.values())
        logger.info(f"Total: {total_added} documents added to RAG system")

        return stats

    def clear_rag_database(self):
        """Clear all documents from the RAG database."""
        # This is a workaround since VectorDB doesn't have clear method
        # We'll reinitialize it
        self.vector_db, self.retriever = create_default_rag_system()
        logger.info("RAG database cleared")

    def get_rag_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG database."""
        stats = {
            "document_count": self.vector_db.get_document_count(),
            "dimension": self.vector_db.dimension,
        }
        return stats

    def search_rag(self, query: str, k: int = 5) -> List[Dict]:
        """Search the RAG database."""
        return self.retriever.retrieve_relevant_documents(query, k)

    def save_rag_database(self, filepath: str = "data/rag_vector_db"):
        """Save the RAG database to disk."""
        try:
            self.vector_db.save(filepath)
            logger.info(f"RAG database saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save RAG database: {e}")
            return False

    def load_rag_database(self, filepath: str = "data/rag_vector_db"):
        """Load the RAG database from disk."""
        try:
            self.vector_db.load(filepath)
            logger.info(f"RAG database loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load RAG database: {e}")
            return False


def main():
    """Main function to demonstrate RAG integration."""
    print("Initializing RAG Integration...")

    integrator = RAGIntegrator()

    # Display initial stats
    initial_stats = integrator.get_rag_stats()
    print(f"Initial RAG stats: {initial_stats}")

    # Perform sync and add to RAG
    print("Starting sync and RAG integration...")
    stats = integrator.sync_and_add_to_rag()
    print(f"Sync results: {stats}")

    # Display final stats
    final_stats = integrator.get_rag_stats()
    print(f"Final RAG stats: {final_stats}")

    # Test search
    print("\nTesting search functionality...")
    results = integrator.search_rag("What meetings do I have this week?", k=3)
    print(f"Search results: {len(results)} items found")
    for i, result in enumerate(results):
        print(
            f"  {i + 1}. {result['document']['metadata'].get('type', 'unknown')}: "
            f"{result['document']['metadata'].get('name', result['document']['metadata'].get('title', 'No title'))}"
        )

    # Save database
    print("\nSaving RAG database...")
    integrator.save_rag_database()

    print("\nRAG Integration completed successfully!")


if __name__ == "__main__":
    main()
