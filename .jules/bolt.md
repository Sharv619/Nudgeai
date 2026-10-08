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

## 2026-03-07 - Pre-Compiled Single-Pass Action Verb Matching in Nudge Extraction
**Learning:** In `clean_action_title()` and `infer_due_date()`, dynamically compiling regexes and sequentially iterating through `ACTION_VERBS` with separate `re.search()` calls created significant overhead on text extraction endpoints (~1240ms / 1000 requests). Pre-compiling a single combined regex `ACTION_VERBS_REGEX = re.compile(r"\b(" + "|".join(...) + r")\b")` at module load time performs a single-pass search across candidate text, reducing extraction latency from ~1.24ms to ~0.34ms per extraction (~3.7x speedup).
**Action:** Pre-compile fixed keyword lists into a single combined `re.compile()` OR pattern at module load time rather than looping through individual keyword regexes dynamically inside hot request handlers.

## 2026-03-08 - Mutation Tracking and Granular Store Access in File-Backed APIs
**Learning:** In file-backed local API servers, unconditionally saving state files on every rule evaluation pass (e.g. `save_rule_state`) and loading all context files (5 JSON reads) when calculating subset status cards creates severe I/O overhead (~410ms / 1000 evaluations). Tracking a `rule_state_changed` boolean before executing `save_rule_state()` and creating a targeted `load_source_status()` helper that reads only required store files reduces evaluation latency by ~3.5x (~409.8ms down to ~153.6ms).
**Action:** Always track state mutations before persisting store objects to disk in hot loop evaluations, and provide targeted store loaders for endpoints that only consume partial context states.

## 2026-03-09 - Single-Pass Datetime Parsing and Array Aggregation in Nudge Summaries
**Learning:** In `nudge_summary()`, calling `matches_due_today()` and `matches_overdue()` separately for each nudge triggered `parse_datetime()` twice on `nudge["dueAt"]`. Additionally, filtering active nudges in a separate list comprehension resulted in multiple iterations over the dataset. Allowing match helpers to accept an optional pre-parsed `due_at` object and accumulating `active_nudges` during the primary iteration loop reduces execution latency by ~30% (~1.4x speedup, from ~1.39ms to ~0.97ms per 100-nudge summary calculation).
**Action:** In summary calculation endpoints, parse date strings once per item and pass pre-parsed `datetime` objects to downstream predicate helpers while accumulating top/active subsets during the primary scan loop.

## 2026-03-10 - Single-Pass Datetime Parsing in MCP Gym Time Suggestion Tool
**Learning:** In `suggest_optimal_gym_time()`, ISO datetime strings were parsed via `datetime.fromisoformat()` repeatedly (up to 4-5 times per event/activity) across filtering, sorting, free slot evaluation, workout hour binning, and tomorrow event filtering loops. Storing pre-parsed `datetime` objects in lightweight tuples `(event_dict, start_dt, end_dt)` during initial file ingestion eliminates redundant ISO string replacements and parsing overhead while keeping JSON-serializable dictionaries clean.
**Action:** When working with timestamped event lists in MCP tools or data pipelines, parse ISO strings into `datetime` objects once during initial record construction and reuse pre-parsed objects in subsequent filtering, sorting, and slot calculation passes.

## 2026-03-11 - Single-Pass FAISS Matrix Search in Batch Semantic Queries
**Learning:** In `RAGMCPIntegrator.batch_semantic_search()`, calling `self.vector_db.search(embedding)` inside a Python `for` loop for each query vector executed separate single-row `index.search()` calls in FAISS. Implementing `VectorDB.batch_search(query_embeddings)` normalizes query embeddings in a single 2D numpy matrix operation and passes the 2D array directly to `self.index.search(normalized_embeddings, k)`, leveraging FAISS's native C++/SIMD multi-vector query processing and achieving a ~4.1x speedup (~2447ms down to ~595ms per 1000 batch searches).
**Action:** Whenever retrieving vector similarity results for multiple query vectors simultaneously, pass the entire 2D matrix of embeddings directly to FAISS `index.search` rather than looping over individual query vectors in Python.

## 2026-03-12 - Reusing Summary Metrics and Single-Pass ISO Parsing in Pattern Recommendations
**Learning:** In `PatternAnalyzer`, calling `_build_calendar_summary()` triggered duplicate ISO timestamp parsing via `_calculate_duration()` and `total_hours_booked` accumulation. Furthermore, downstream recommendation generation in `_generate_recommendations()` re-parsed all calendar timestamps and re-iterated location and fitness result sets from scratch. Consolidating ISO string parsing into a single pass inside `_build_calendar_summary()` and passing pre-computed summary dicts (`calendar_summary`, `location_summary`, `fitness_summary`) to `_generate_recommendations()` reduces recommendation computation latency by ~2.1x (~347ms down to ~164ms per 1000 summary calculations).
**Action:** When generating analytics or recommendations downstream of summary builders, pass the pre-computed summary objects to avoid redundant list iterations and timestamp parsing on raw search result payloads.
