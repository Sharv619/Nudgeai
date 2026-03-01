"""
RAG System for NudgeAI - Main Module

This module provides the core RAG (Retrieval-Augmented Generation) functionality
for the NudgeAI personal productivity assistant.
"""

from .embedding.generate import generate_embedding, generate_embeddings
from .indexing.vector_db import VectorDB
from .retrieval.search import RAGRetriever, create_rag_pipeline

__all__ = [
    "generate_embedding",
    "generate_embeddings",
    "VectorDB",
    "RAGRetriever",
    "create_rag_pipeline",
]


def create_default_rag_system():
    """
    Create a default RAG system with standard configuration.

    Returns:
        Tuple of (VectorDB, RAGRetriever) instances
    """
    vector_db = VectorDB()
    retriever = create_rag_pipeline(vector_db)
    return vector_db, retriever


# Version information
__version__ = "1.0.0"
__author__ = "NudgeAI RAG System"
