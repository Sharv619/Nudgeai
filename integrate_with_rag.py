#!/usr/bin/env python3
"""
Simple RAG integration that processes the synced data
"""

import json
import os
from pathlib import Path
from datetime import datetime

def load_synced_data():
    """Load the synced data from JSON files"""
    data_dir = Path("data_sync")
    if not data_dir.exists():
        print("❌ No synced data found. Please run data sync first.")
        return None
    
    synced_data = {}
    for file in data_dir.glob("*_sync.json"):
        source = file.stem.replace("_sync", "")
        with open(file, 'r') as f:
            synced_data[source] = json.load(f)
    
    return synced_data

def create_rag_documents(synced_data):
    """Create RAG documents from synced data"""
    documents = []
    
    for source, data in synced_data.items():
        for item in data:
            doc = {
                "id": item["id"],
                "text": item["text"],
                "metadata": item["metadata"]
            }
            documents.append(doc)
    
    return documents

def save_rag_data(documents):
    """Save RAG-processed data"""
    rag_dir = Path("rag_data")
    rag_dir.mkdir(exist_ok=True)
    
    # Save documents
    docs_file = rag_dir / "documents.json"
    with open(docs_file, 'w') as f:
        json.dump(documents, f, indent=2)
    
    # Create summary
    summary = {
        "total_documents": len(documents),
        "sources": list(set(doc["metadata"]["type"] for doc in documents)),
        "processed_at": datetime.now().isoformat() + "Z",
        "document_types": {}
    }
    
    # Count by type
    for doc in documents:
        doc_type = doc["metadata"]["type"]
        if doc_type not in summary["document_types"]:
            summary["document_types"][doc_type] = 0
        summary["document_types"][doc_type] += 1
    
    # Save summary
    summary_file = rag_dir / "rag_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary

def main():
    """Main function to integrate synced data with RAG"""
    print("🔗 Starting RAG Integration...")
    
    # Load synced data
    print("📂 Loading synced data...")
    synced_data = load_synced_data()
    if not synced_data:
        return False
    
    # Create RAG documents
    print("📝 Creating RAG documents...")
    documents = create_rag_documents(synced_data)
    
    # Save RAG data
    print("💾 Saving RAG-processed data...")
    summary = save_rag_data(documents)
    
    print(f"\n✅ RAG integration completed successfully!")
    print(f"📊 Summary:")
    print(f"   - Total documents: {summary['total_documents']}")
    print(f"   - Document types: {', '.join(summary['sources'])}")
    for doc_type, count in summary['document_types'].items():
        print(f"   - {doc_type}: {count} documents")
    print(f"📁 Files saved to: rag_data/")
    
    return True

if __name__ == "__main__":
    main()