# NudgeAI Roadmap & Tasks

This document outlines the planned tasks for Phase 3 and beyond.

## Phase 3: Predictive Analytics & Proactive Nudging (Current Focus)

- [ ] **Predictive Modeling**
    - Implement time-series analysis for user activity prediction.
    - Develop "Expected Arrival" and "Next Likely Action" models.
    - Integrate predictive insights into the RAG retrieval flow.

- [ ] **Enhanced Proactive Nudging**
    - Implement "Pre-emptive Nudges" (suggestions before a conflict occurs).
    - Add support for more location types and custom user-defined geofences.
    - Develop a priority system for multiple simultaneous nudge opportunities.

- [ ] **Habit Reinforcement Mechanisms**
    - Create a "Streak Tracking" system for identified positive habits.
    - Implement "Micro-nudges" for habit formation (e.g., hydration, standing).
    - Develop habit-specific progress visualizations.

- [ ] **AI Assistant Pattern-Awareness**
    - Update the MCP prompt templates to be more "pattern-aware".
    - Allow the LLM to reference historical trends during live conversations.

## Phase 4: Frontend & User Experience

- [ ] **Real-time Dashboard**
    - Build a web interface to display daily/weekly summaries.
    - Implement interactive charts for fitness and productivity trends.
    - Create a "Nudge Feed" for reviewing past and upcoming suggestions.

- [ ] **Settings & Configuration UI**
    - Interface for managing Google API connections.
    - UI for defining "Important Locations" and nudge preferences.
    - Integration with WhiteCircle for user-level quality threshold settings.

## Future Improvements & Maintenance

- [ ] **Performance Optimization**
    - Optimize FAISS indexing for larger datasets.
    - Implement caching for frequent LLM synthesis requests.
- [ ] **Security & Privacy**
    - Enhanced encryption for local data storage.
    - More granular permission controls for data ingestion.
- [ ] **Expanded Integrations**
    - Support for additional data sources (e.g., Slack, Notion, Spotify).
    - Mobile app integration for push notification nudges.
- [ ] **Testing & Robustness**
    - Increase unit test coverage for `ragsystem/`.
    - Implement end-to-end integration tests for the full nudge pipeline.
