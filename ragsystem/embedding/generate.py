from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union

# Load the embedding model (lightweight and fast)
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str):
    """Convert text to a vector embedding."""
    return model.encode(text)


def generate_embeddings(texts: List[str]):
    """Convert multiple texts to vector embeddings."""
    return model.encode(texts)


if __name__ == "__main__":
    print("Testing embedding generation...")
    test_embedding = generate_embedding("Meeting with Alex at 3 PM")
    print(f"Embedding shape: {test_embedding.shape}")
    print(f"First 5 dimensions: {test_embedding[:5]}")  # Print first 5 dims

    # Test multiple embeddings
    test_texts = [
        "Meeting with Alex at 3 PM",
        "Gym session tomorrow morning",
        "Review quarterly reports",
    ]
    embeddings = generate_embeddings(test_texts)
    print(f"Multiple embeddings shape: {embeddings.shape}")
    print("Successfully generated embeddings!")
