import numpy as np
from typing import List, Dict, Any, Optional
from ..embedding.generate import generate_embedding
from ..indexing.vector_db import VectorDB


class RAGRetriever:
    """
    Retrieval component for the RAG system that handles searching and retrieving
    relevant documents based on user queries.
    """

    def __init__(self, vector_db: VectorDB):
        """
        Initialize the RAG retriever.

        Args:
            vector_db: Initialized VectorDB instance
        """
        self.vector_db = vector_db

    def retrieve_relevant_documents(
        self, query: str, k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a given query.

        Args:
            query: User query string
            k: Number of documents to retrieve

        Returns:
            List of relevant documents with metadata and similarity scores
        """
        # Generate embedding for the query
        query_embedding = generate_embedding(query)

        # Search for similar documents in the vector database
        results = self.vector_db.search(query_embedding, k=k)

        return results

    def retrieve_and_format_context(self, query: str, k: int = 5) -> str:
        """
        Retrieve relevant documents and format them as context for the LLM.

        Args:
            query: User query string
            k: Number of documents to retrieve

        Returns:
            Formatted context string containing relevant documents
        """
        results = self.retrieve_relevant_documents(query, k)

        # Format results as a context string
        context_parts = []
        context_parts.append("Relevant documents found for your query:\n")

        for i, result in enumerate(results, 1):
            doc_metadata = result["document"]["metadata"]
            similarity_score = result["similarity_score"]

            context_part = f"Document {i} (Similarity: {similarity_score:.3f}):\n"
            context_part += f"- Title: {doc_metadata.get('title', 'N/A')}\n"
            context_part += f"- Type: {doc_metadata.get('type', 'N/A')}\n"
            context_part += f"- Summary: {doc_metadata.get('summary', 'N/A')}\n"

            # Add other metadata fields if they exist
            for key, value in doc_metadata.items():
                if key not in ["title", "type", "summary"]:
                    context_part += f"- {key.title()}: {value}\n"

            context_part += "\n"
            context_parts.append(context_part)

        return "".join(context_parts)

    def retrieve_top_k_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve top-k most relevant documents with detailed information.

        Args:
            query: User query string
            k: Number of documents to retrieve

        Returns:
            List of top-k documents with full information
        """
        results = self.retrieve_relevant_documents(query, k)

        # Enhance results with additional context
        enhanced_results = []
        for result in results:
            enhanced_result = {
                "document_id": result["document"]["id"],
                "metadata": result["document"]["metadata"],
                "similarity_score": result["similarity_score"],
                "relevance_explanation": f"This document has a similarity score of {result['similarity_score']:.3f} "
                f"to your query: '{query}'",
            }
            enhanced_results.append(enhanced_result)

        return enhanced_results


def create_rag_pipeline(vector_db: Optional[VectorDB] = None) -> RAGRetriever:
    """
    Factory function to create a RAG pipeline with a vector database.

    Args:
        vector_db: Pre-initialized VectorDB instance (creates new one if None)

    Returns:
        RAGRetriever instance
    """
    if vector_db is None:
        vector_db = VectorDB()

    return RAGRetriever(vector_db)


# Example usage and testing
if __name__ == "__main__":
    print("Testing RAG Retriever functionality...")

    # Create a vector database and add some sample documents
    db = VectorDB()

    # Sample documents with different contexts
    sample_docs = [
        {
            "id": "calendar_001",
            "content": "Team meeting scheduled for 3 PM in Conference Room A to discuss Q4 goals",
            "metadata": {
                "title": "Team Meeting",
                "type": "calendar_event",
                "summary": "Q4 goals discussion",
                "date": "2024-01-15",
                "attendees": ["john@example.com", "jane@example.com"],
            },
        },
        {
            "id": "habit_001",
            "content": "Gym session every Monday, Wednesday, Friday at 6 AM",
            "metadata": {
                "title": "Morning Workout Routine",
                "type": "habit",
                "summary": "Consistent exercise schedule",
                "frequency": "3 times per week",
                "time": "6:00 AM",
            },
        },
        {
            "id": "document_001",
            "content": "Project budget proposal for the new marketing campaign",
            "metadata": {
                "title": "Marketing Campaign Budget",
                "type": "document",
                "summary": "Financial planning for marketing initiative",
                "category": "finance",
                "status": "draft",
            },
        },
    ]

    # Add documents to the database using embeddings
    for doc in sample_docs:
        embedding = generate_embedding(doc["content"])
        db.add_document(doc["id"], embedding, doc["metadata"])

    print(f"Created database with {db.get_document_count()} documents")

    # Create the retriever
    retriever = create_rag_pipeline(db)

    # Test retrieval with a query
    query = "What meetings are scheduled for today?"
    results = retriever.retrieve_relevant_documents(query, k=2)

    print(f"\nQuery: '{query}'")
    print(f"Found {len(results)} relevant documents:")
    for i, result in enumerate(results):
        print(
            f"  {i + 1}. Doc ID: {result['document']['id']}, Score: {result['similarity_score']:.4f}"
        )

    # Test formatted context
    formatted_context = retriever.retrieve_and_format_context(query, k=2)
    print(f"\nFormatted context:\n{formatted_context}")

    # Test top-k retrieval
    top_k_results = retriever.retrieve_top_k_documents(query, k=2)
    print(f"Top-K retrieval test completed with {len(top_k_results)} results")

    print("\nRAG Retriever functionality test completed successfully!")
