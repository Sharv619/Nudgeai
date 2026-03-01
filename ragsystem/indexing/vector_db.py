import faiss
import numpy as np
from typing import List, Dict, Any, Optional
import pickle
import os
from pathlib import Path

# Type aliases for better readability
FaissIndex = Any  # FAISS index type (using Any since FAISS types can vary)


class VectorDB:
    """
    A vector database using FAISS for efficient similarity search of embedded documents.
    """

    def __init__(self, dimension: int = 384):
        """
        Initialize the vector database.

        Args:
            dimension: Dimension of the embeddings (384 for all-MiniLM-L6-v2)
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.documents: List[Dict[str, Any]] = []  # Store document metadata
        self.doc_ids: List[str] = []  # Store document IDs

    def add_document(
        self, doc_id: str, embedding: np.ndarray, metadata: Dict[str, Any]
    ) -> None:
        """
        Add a document to the vector database.

        Args:
            doc_id: Unique identifier for the document
            embedding: Vector embedding of the document
            metadata: Additional metadata about the document
        """
        # Validate embedding dimension
        if len(embedding) != self.dimension:
            raise ValueError(
                f"Embedding dimension {len(embedding)} != expected {self.dimension}"
            )

        # Normalize the embedding for cosine similarity
        normalized_embedding = embedding / np.linalg.norm(embedding)

        # Add to FAISS index
        embedding_array = normalized_embedding.reshape(1, -1).astype(np.float32)
        # FAISS expects a 2D array with shape (n, d) where n is number of vectors and d is dimensions
        self.index.add(embedding_array)  # type: ignore[union-attr]

        # Store metadata
        self.documents.append({"id": doc_id, "metadata": metadata})
        self.doc_ids.append(doc_id)

    def add_documents(
        self,
        doc_ids: List[str],
        embeddings: np.ndarray,
        metadatas: List[Dict[str, Any]],
    ):
        """
        Add multiple documents to the vector database efficiently.

        Args:
            doc_ids: List of unique identifiers
            embeddings: Array of embeddings (n_docs x embedding_dim)
            metadatas: List of metadata dictionaries
        """
        # Validate embeddings dimension
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension {embeddings.shape[1]} != expected {self.dimension}"
            )

        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
        normalized_embeddings = embeddings / norms

        # Add to FAISS index
        self.index.add(normalized_embeddings.astype(np.float32))  # type: ignore[union-attr]

        # Store metadata
        for doc_id, metadata in zip(doc_ids, metadatas):
            self.documents.append({"id": doc_id, "metadata": metadata})
            self.doc_ids.append(doc_id)

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents to the query embedding.

        Args:
            query_embedding: Embedding to search for similar documents
            k: Number of results to return

        Returns:
            List of dictionaries containing document info and similarity scores
        """
        # Validate query embedding dimension
        if len(query_embedding) != self.dimension:
            raise ValueError(
                f"Query dimension {len(query_embedding)} != expected {self.dimension}"
            )

        # Normalize query embedding
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        try:
            # Perform similarity search
            distances, indices = self.index.search(  # type: ignore[union-attr, arg-type]
                query_embedding.reshape(1, -1).astype(np.float32), k
            )

            # Format results
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx >= 0 and idx < len(self.documents):  # Valid index
                    result = {
                        "document": self.documents[idx],
                        "similarity_score": float(distance),
                        "index": int(idx),
                    }
                    results.append(result)

            return results

        except Exception as e:
            print(f"FAISS search error: {str(e)}")
            return []  # Graceful fallback

    def save(self, filepath: str):
        """
        Save the vector database to disk.

        Args:
            filepath: Path to save the database
        """
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        data = {
            "documents": self.documents,
            "doc_ids": self.doc_ids,
            "dimension": self.dimension,
        }

        # Save FAISS index separately (since it's a C object)
        faiss.write_index(self.index, f"{filepath}.index")

        # Save metadata using pickle
        with open(filepath, "wb") as f:
            pickle.dump(data, f)

    def load(self, filepath: str):
        """
        Load the vector database from disk.

        Args:
            filepath: Path to load the database from
        """
        # Load FAISS index
        self.index = faiss.read_index(f"{filepath}.index")

        # Load metadata
        with open(filepath, "rb") as f:
            data = pickle.load(f)

        self.documents = data["documents"]
        self.doc_ids = data["doc_ids"]
        self.dimension = data["dimension"]

    def get_document_count(self) -> int:
        """Return the number of documents in the database."""
        return len(self.documents)


# Example usage and testing
if __name__ == "__main__":
    print("Testing VectorDB functionality...")

    # Create a vector database
    db = VectorDB()

    # Sample embeddings (these would normally come from the embedding module)
    # Using random vectors for testing
    np.random.seed(42)  # For reproducible results
    sample_embeddings = np.random.rand(3, 384).astype("float32")

    # Add sample documents
    sample_docs = [
        {
            "id": "doc1",
            "embedding": sample_embeddings[0],
            "metadata": {
                "title": "Meeting Notes",
                "type": "calendar",
                "summary": "Team meeting discussing project timeline",
            },
        },
        {
            "id": "doc2",
            "embedding": sample_embeddings[1],
            "metadata": {
                "title": "Gym Schedule",
                "type": "habit",
                "summary": "Weekly gym sessions and fitness goals",
            },
        },
        {
            "id": "doc3",
            "embedding": sample_embeddings[2],
            "metadata": {
                "title": "Project Report",
                "type": "document",
                "summary": "Quarterly report with financial metrics",
            },
        },
    ]

    # Add documents to the database
    for doc in sample_docs:
        db.add_document(doc["id"], doc["embedding"], doc["metadata"])

    print(f"Added {db.get_document_count()} documents to the database")

    # Test search with a query embedding
    query_embedding = np.random.rand(384).astype("float32")
    results = db.search(query_embedding, k=2)

    print(f"Search returned {len(results)} results:")
    for i, result in enumerate(results):
        print(
            f"  {i + 1}. Doc ID: {result['document']['id']}, Score: {result['similarity_score']:.4f}"
        )

    # Test saving/loading
    db.save("test_vector_db")
    print("Database saved successfully")

    # Create a new database and load the saved one
    new_db = VectorDB()
    new_db.load("test_vector_db")
    print(f"Loaded database with {new_db.get_document_count()} documents")

    print("VectorDB functionality test completed successfully!")
