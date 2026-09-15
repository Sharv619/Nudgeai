## 2026-03-01 - Batch Vectorization and Indexing in RAG Ingestion
**Learning:** In SentenceTransformers + FAISS RAG ingestion pipelines, invoking `generate_embeddings(texts)` and `VectorDB.add_documents()` in batches processes matrix calculations via vectorized operations in a single forward pass, providing a ~5.3x speedup compared to sequential single-item processing.
**Action:** Always prefer batch vectorization and bulk vector DB insertion when indexing multi-document lists, while providing fallback logic for individual item errors if needed.

## 2026-03-02 - Batch Semantic Query Embedding in Pattern Analysis
**Learning:** Performing multiple individual semantic searches sequentially (e.g. searching calendar, location, and fitness data separately) creates a bottleneck by invoking separate SentenceTransformer forward passes for each query string. Providing a `batch_semantic_search` helper that batches query strings into `generate_embeddings([q1, q2, q3])` computes query vector embeddings in a single GPU/CPU matrix operation pass, yielding a ~2.7x speedup (~59.4ms down to ~22.0ms per pattern analysis run).
**Action:** When an analytical or reporting component executes multiple semantic searches across data sources or facets, batch the query strings and generate query embeddings together before executing vector DB lookups.

## 2026-03-03 - Batch Semantic Search in MCP Personal Insights Tool
**Learning:** In MCP tool handlers like `get_personal_insights`, multi-source data retrieval (`calendar`, `location`, `drive`) using sequential `semantic_search` calls incurs redundant model forward passes. Batching search queries using `rag_mcp_integrator.batch_semantic_search` reduces query processing latency by ~2.2x (~37.2ms down to ~16.5ms) while preserving output structures and match filtering.
**Action:** Always check MCP tools that perform queries across multiple domain sources and replace sequential search calls with `batch_semantic_search`.

## 2026-03-04 - Batching Multi-Day RAG Queries in Weekly Summaries
**Learning:** In `DailySummarizer.generate_weekly_summary`, iteratively calling `generate_daily_summary` for 7 days executed 21 individual RAG semantic searches sequentially (7 days x 3 queries per day), invoking 21 separate model forward passes. Constructing a single list of 21 search request tuples and executing `rag_mcp_integrator.batch_semantic_search` processes all query vectorizations in a single forward pass, reducing weekly summary generation latency from ~126ms to ~46ms (~2.7x speedup).
**Action:** When aggregating multi-period summaries or reports over range intervals, construct a unified list of query requests across all periods and issue a single `batch_semantic_search` call.

## 2026-03-05 - Batching Location Pattern Searches in Location Nudger
**Learning:** In `LocationNudger.update_important_locations_from_data`, sequentially calling `location_pattern_search` for different location types ('home', 'work') invoked separate embedding model passes. Combining search requests into `rag_mcp_integrator.batch_semantic_search` computes embedding vectors for all search patterns in a single matrix pass, reducing location update latency by ~1.7x (~25.0ms down to ~14.5ms).
**Action:** When location-aware or context-updating services need to retrieve patterns for multiple place types or categories, batch the pattern query requests into a single `batch_semantic_search` call.

## 2026-03-06 - Short-Circuiting Semantic Conflict Queries in Location Nudging
**Learning:** In `LocationNudger.generate_location_nudge`, invoking `get_current_conflicts()` before validating whether nearby locations contain non-empty `conflict_keywords` forced unnecessary RAG semantic searches on calendar events (~14.7ms per evaluation). Checking if any matched nearby location actually specifies conflict keywords before invoking `get_current_conflicts()` eliminates expensive embedding passes when no conflict filtering criteria exist, reducing evaluation time from ~14.7ms to ~0.015ms.
**Action:** Always check if filtering/conflict criteria are defined before triggering costly vector retrieval or semantic search routines.
