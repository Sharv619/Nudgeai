## 2026-03-01 - Batch Vectorization and Indexing in RAG Ingestion
**Learning:** In SentenceTransformers + FAISS RAG ingestion pipelines, invoking `generate_embeddings(texts)` and `VectorDB.add_documents()` in batches processes matrix calculations via vectorized operations in a single forward pass, providing a ~5.3x speedup compared to sequential single-item processing.
**Action:** Always prefer batch vectorization and bulk vector DB insertion when indexing multi-document lists, while providing fallback logic for individual item errors if needed.

## 2026-03-02 - Batch Semantic Query Embedding in Pattern Analysis
**Learning:** Performing multiple individual semantic searches sequentially (e.g. searching calendar, location, and fitness data separately) creates a bottleneck by invoking separate SentenceTransformer forward passes for each query string. Providing a `batch_semantic_search` helper that batches query strings into `generate_embeddings([q1, q2, q3])` computes query vector embeddings in a single GPU/CPU matrix operation pass, yielding a ~2.7x speedup (~59.4ms down to ~22.0ms per pattern analysis run).
**Action:** When an analytical or reporting component executes multiple semantic searches across data sources or facets, batch the query strings and generate query embeddings together before executing vector DB lookups.

## 2026-03-03 - Batch Semantic Search in Daily Summary Generation
**Learning:** In `generate_daily_summary`, querying calendar, location, and fitness data via individual `semantic_search` calls required 3 separate model forward passes per summary. Using `batch_semantic_search` reduces forward passes by 3x, yielding a ~2.1x speedup for daily summaries (~31.3ms down to ~14.6ms) and a ~2.6x speedup for weekly summaries (~257.9ms down to ~99.0ms).
**Action:** In summary and reporting routines that retrieve multiple data facets for a date or period, leverage `batch_semantic_search` to evaluate query vector embeddings in a single forward pass.
