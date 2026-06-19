# NudgeAI Deep Audit

Audit date: 2026-06-18

## 1. Executive Summary

NudgeAI has moved from a data/RAG prototype toward a coherent local-first personal nudge platform. The current canonical product path is the React/Vite dashboard backed by `simple_api_server.py`, with local JSON persistence and explicit privacy guardrails. The manual nudge lifecycle, local context automation, AI extraction review flow, and browser notification layer are now implemented in the local MVP path.

The completed platform capabilities are:

- Manual nudge CRUD with persisted local JSON storage.
- Nudge lifecycle states: `pending`, `snoozed`, `completed`, and `dismissed`.
- Due-today and overdue computation for dashboard grouping and notification eligibility.
- Local places and context rules, including the first `Gym Opportunity` rule.
- Local automation controls for browser geolocation and context-rule polling while the dashboard is open.
- Backend-owned notification evaluation through `GET /api/notifications/poll`.
- Browser-native desktop notifications through the Web Notification API, without any cloud push relay.
- AI-assisted extraction through `POST /api/extract`, with Pydantic validation, deterministic rule fallback, and optional local/cloud LLM hooks.
- Git-index privacy guardrails through `scripts/privacy_check.py`.
- A CI workflow covering Python syntax, backend tests, privacy guard, and frontend production build.

The Local Automation and AI Extraction sprints are complete at the local prototype level. The platform is not production-ready because it still has no application authentication, no user isolation, permissive CORS, local JSON persistence, no concurrent write protection, no deployment hardening, and experimental legacy paths that can still expose sensitive local data if misused.

The strongest architectural achievement is that the active intelligence layer remains local-first and backend-mediated. The frontend asks for browser permissions and renders UX, but the backend owns nudge state, extraction validation, context-rule evaluation, and notification eligibility. This improves future Flutter migration readiness because native clients can reuse the same REST contracts.

## 2. Architectural Topology Map

```text
                         Local User Machine
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  React / Vite Frontend                                               │
│  frontend/src/pages/Dashboard.jsx                                    │
│                                                                      │
│  ┌──────────────────────┐    ┌────────────────────────────────────┐  │
│  │ Manual Nudge UI      │    │ Browser APIs                       │  │
│  │ - create             │    │ - navigator.geolocation            │  │
│  │ - complete           │    │ - Web Notification API             │  │
│  │ - snooze             │    │ - window focus / scroll highlight  │  │
│  │ - dismiss            │    └────────────────────────────────────┘  │
│  │ - delete             │                                             │
│  └──────────┬───────────┘                                             │
│             │                                                         │
│             │ /api via Vite proxy                                     │
│             v                                                         │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │ FastAPI Canonical MVP Backend                                  │   │
│  │ simple_api_server.py                                           │   │
│  │                                                                │   │
│  │  Nudge CRUD:             /api/nudges                           │   │
│  │  Extraction:             /api/extract                          │   │
│  │  Context state:          /api/context                          │   │
│  │  Places/rules:           /api/places, /api/context-rules       │   │
│  │  Rule evaluation:        /api/context-rules/evaluate           │   │
│  │  Notification delta:     /api/notifications/poll               │   │
│  │                                                                │   │
│  │  ┌─────────────────────┐    ┌───────────────────────────────┐  │   │
│  │  │ Local JSON Stores   │    │ AI Extraction Engine          │  │   │
│  │  │ - data/nudges.json  │    │ - Pydantic schemas            │  │   │
│  │  │ - data/places.json  │    │ - deterministic rules         │  │   │
│  │  │ - data/rules.json   │    │ - optional local LLM endpoint │  │   │
│  │  │ - rule_state.json   │    │ - opt-in external LLM         │  │   │
│  │  │ - current_location  │    └───────────────────────────────┘  │   │
│  │  │ - calendar free min │                                       │   │
│  │  └─────────────────────┘                                       │   │
│  └────────────────────────────────────────────────────────────────┘   │
│             │                                                         │
│             │ experimental only                                       │
│             v                                                         │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │ MCP / RAG Experimental Bridge                                  │   │
│  │ mcp_api_bridge.py, mcp_server.py, ragsystem/                   │   │
│  │ - not canonical MVP runtime                                    │   │
│  │ - exposes local RAG/MCP tools over HTTP                        │   │
│  │ - depends on provider tokens and local sync artifacts           │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Core Runtime Roles

| Component | Current Role | Architectural Status |
|---|---|---|
| `simple_api_server.py` | Canonical FastAPI backend for the local MVP. Owns nudge CRUD, local context stores, context rule evaluation, AI extraction, notification eligibility, and experimental data endpoints. | Primary runtime path. |
| `frontend/src/pages/Dashboard.jsx` | Frontend state machine for manual nudges, messy-review extraction, local automation, place/rule editing, and Web Notification dispatch. | Primary user interface. |
| `frontend/src/utils/api.js` | Axios API client targeting `/api` through the Vite proxy. Exposes `nudgeApi`, `contextApi`, and legacy `mcpApi`. | Shared API adapter. |
| `mcp_api_bridge.py` | HTTP bridge to the MCP/RAG server and local data tools. | Experimental/legacy path, not required for the local nudge MVP. |
| `scripts/privacy_check.py` | Git-index guard that prevents forbidden private files from being tracked. | Required pre-commit/CI privacy control. |
| `data/demo/*` | Sanitized public-demo fixtures. | Safe checked-in demo data boundary. |

## 3. Technical Security & Privacy Assessment

### Data Sovereignty Model

NudgeAI's current MVP is intentionally local-first. The primary data stores are JSON files under `data/`, including nudges, places, context rules, rule state, current location, and calendar availability. These local stores are ignored by `.gitignore` and treated as private user artifacts.

The data sovereignty guarantees are operational rather than cryptographic:

- Core nudge CRUD does not require cloud services.
- Browser geolocation is opt-in and only requested while the dashboard is open.
- Context-rule polling runs in the browser through visible UI toggles.
- Desktop notifications use the browser Web Notification API only.
- `GET /api/notifications/poll` emits raw local alert payloads and marks them as notified in local JSON.
- No Firebase Cloud Messaging, OneSignal, hosted push relay, or background cloud notification transport is used.
- AI extraction defaults to deterministic local rule parsing when provider configuration is absent or disabled.
- External LLM use requires explicit environment opt-in through `EXTRACT_ALLOW_EXTERNAL_LLM=true` and provider keys.

This model is suitable for a local prototype and portfolio demo. It is not sufficient for hosted multi-user production because there is no authentication, authorization, tenant boundary, encryption-at-rest strategy, data retention policy, or controlled CORS policy.

### Web Notification API Boundary

The Web Notification integration is local to the browser runtime:

- Permission is requested through `Notification.requestPermission()`.
- Alerts are rendered by `new Notification(title, { body, tag })`.
- Notification clicks call `window.focus()` and scroll/highlight the matching dashboard card.
- The backend does not know about browser rendering details beyond raw alert fields.
- The backend alert contract can be reused by a native client because it returns generic `{ id, title, body, type }` objects.

The privacy boundary is strong for local use because notification dispatch never leaves the local browser/OS stack. The risk is that notification text can appear in OS-level notification history or lock-screen surfaces depending on the user's operating system settings. This should be documented before public release.

### AI Extraction Privacy Boundary

`POST /api/extract` accepts `{ "text_content": "..." }` and returns review-only suggestions. It does not save extracted suggestions automatically. Persistence only happens after the user approves a suggestion through the existing nudge creation endpoint.

The extraction layer includes:

- `ExtractRequest` for input validation.
- `ExtractedSuggestion` for output validation.
- `jsonable_encoder` in the shared validation exception handler to safely serialize Pydantic validation details.
- A deterministic parser for local fallback.
- A prompt that instructs LLMs not to store, train on, exfiltrate, or reveal user data.
- Local LLM support through `EXTRACT_LOCAL_LLM_URL`.
- OpenAI/Mistral-compatible provider hooks guarded by `EXTRACT_ALLOW_EXTERNAL_LLM`.

The privacy posture is appropriate for local-first development because the default `.env.example` sets `EXTRACT_LLM_PROVIDER=rules` and `EXTRACT_ALLOW_EXTERNAL_LLM=false`. If a developer enables external LLMs, pasted notes can leave the machine. That transition should require product-level disclosure, provider retention review, and explicit user consent.

### Demo Fixture Isolation

The repository separates safe public demo data from private runtime data:

- Sanitized fixtures are checked in under `data/demo/`.
- Local private stores such as `data/nudges.json`, `data/places.json`, `data/context_rules.json`, `data/rule_state.json`, `data/current_location.json`, and `data/calendar_availability.json` are ignored.
- Real Google sync outputs such as `calendar_events.json`, `drive_documents.json`, and `data_sync/*.json` are forbidden from the git index by policy and by `scripts/privacy_check.py`.

Current read-only audit found no forbidden private artifacts in `git ls-files`. Local private artifacts may still exist on disk, but the privacy guard treats that as acceptable when they are ignored and untracked.

### Privacy Guard Mechanics

`scripts/privacy_check.py` checks a fixed set of forbidden paths with `git ls-files`. It fails if any forbidden private artifact is tracked by the git index. It warns when those files exist locally but are ignored/untracked.

This design matches the intended local-first workflow:

```text
local private file exists on disk
    -> allowed if ignored/untracked
    -> blocked if present in git ls-files
```

The guard explicitly covers:

- `api/env.local`
- `token.json`
- `drive_token.json`
- `calendar_events.json`
- `drive_documents.json`
- `drive_documents_rag.json`
- `data_sync/calendar_sync.json`
- `data_sync/drive_sync.json`
- `data_sync/sync_summary.json`

The correct remediation remains `git rm --cached <path>`, which removes tracked index entries without deleting the local file.

### Security Risks Remaining

| Risk | Severity | Current State | Recommendation |
|---|---|---|---|
| No app authentication | High | Single-user local mode only. | Add auth before hosting or sharing user data. |
| Open CORS | High | `allow_origins=["*"]` exists in `simple_api_server.py` and experimental APIs. | Restrict per environment before deployment. |
| Local JSON race conditions | Medium | File writes are simple `write_text` operations. | Add file locks or migrate to SQLite for concurrent clients. |
| External LLM data egress | Medium/High | Disabled by default, but supported by env vars. | Add explicit user consent and provider retention documentation. |
| OS notification disclosure | Medium | Browser notifications may appear in system UI. | Add user-facing privacy note for notification content. |
| Legacy experimental routes | Medium | MCP/RAG/data pages remain accessible in repo/UI. | Keep labeled experimental or isolate behind feature flags. |
| Logs and generated files | Medium | Repo still contains historical logs and generated artifacts. | Move runtime logs out of versioned paths. |

## 4. Unit Testing & Compliance Ledger

### Test Suite Scope

The Python unit suite currently contains 21 tests across three files:

| Test File | Count | Coverage Area |
|---|---:|---|
| `tests/test_nudge_store.py` | 2 | Local nudge JSON save/load behavior and empty-store handling. |
| `tests/test_nudge_api.py` | 11 | Nudge CRUD, validation errors, AI extraction, context source state, place/rule updates, notification polling, notification reset behavior, and Gym Opportunity API behavior. |
| `tests/test_context_rules.py` | 8 | Haversine distance, place proximity, calendar availability, time-window logic, cooldown behavior, and rule-created nudge duplication prevention. |

### Verified Compliance Commands

The current CI and local verification pipeline is:

```bash
python -m py_compile simple_api_server.py mcp_api_bridge.py
python -m unittest tests.test_nudge_store tests.test_nudge_api tests.test_context_rules
python scripts/privacy_check.py
cd frontend && npm run build
```

Recent verification status from the implementation pass:

| Check | Result | Notes |
|---|---|---|
| Backend syntax compilation | Green | `simple_api_server.py` and `mcp_api_bridge.py` compile. |
| Python unit tests | Green | 21 tests pass. |
| Privacy guard | Green | No forbidden private artifacts are tracked by git. |
| Frontend production build | Green with warning | Build succeeds; Vite reports a large chunk warning. |

### CI Workflow

`.github/workflows/ci.yml` mirrors the local verification steps:

- Sets up Python 3.11.
- Installs minimal FastAPI/Pydantic/httpx/uvicorn dependencies for tests.
- Compiles `simple_api_server.py` and `mcp_api_bridge.py`.
- Runs the three Python unit test modules.
- Runs `scripts/privacy_check.py`.
- Sets up Node 20.
- Runs `npm ci` and `npm run build` in `frontend/`.

This is an appropriate baseline CI gate for the local MVP. It does not yet include frontend unit tests, browser automation, linting, static type checks, security scanning, or dependency vulnerability auditing.

## 5. Identified Technical Debt & Scaling Risks

### 5.1 Frontend Large Chunk Warning

The Vite production build succeeds but warns that some chunks exceed 500 kB after minification. The most likely contributors are all-routes-in-one bundling and heavy dashboard-adjacent dependencies such as FullCalendar, Chart.js, and legacy experimental visualization pages.

Risk:

- Slower initial load.
- Poorer mobile startup performance.
- More expensive future Flutter Web or PWA packaging if the browser surface expands.

Recommended mitigation:

- Lazy-load experimental routes such as calendar, data visualization, and tools.
- Split dashboard-only code from MCP/RAG/demo pages.
- Consider `manualChunks` only after route-level code splitting is in place.

### 5.2 Client-Side Polling Performance Signature

The dashboard uses fixed 60-second intervals for browser geolocation, context-rule polling, and notification polling. This is acceptable for localhost and a single open dashboard tab. It is not suitable as-is for multi-tab, hosted, or mobile background execution.

Risk:

- Duplicate polling from multiple tabs.
- Extra local file writes if context rules trigger repeatedly.
- Notification polling marks alerts as notified when fetched, so clients should only call it when ready to dispatch notifications.
- Native mobile background tasks will need platform-specific scheduling and battery constraints.

Recommended mitigation:

- Add a local client identifier or lease if multi-tab behavior matters.
- Add settings for polling intervals.
- Consider ETags, cursors, or `since` timestamps for future delta APIs.
- For Flutter, move polling into explicit background task boundaries and reuse the backend `GET /api/notifications/poll` contract.

### 5.3 Volatile Extraction Review Queue

The AI extraction review queue lives in React component state. Suggestions disappear on page reload, navigation, or tab closure unless approved into real nudges.

Risk:

- User may lose unapproved extracted suggestions.
- No audit trail for discarded suggestions.
- No recovery if the browser crashes after extraction but before approval.

Recommended mitigation:

- Persist extraction sessions locally only after privacy review.
- Alternatively keep volatility as a deliberate privacy feature and clearly label it.
- If persisted, store only minimal metadata and support deletion.

### 5.4 Local JSON Persistence Limits

Local JSON is effective for a prototype but has scaling limits:

- No transactional writes.
- No concurrent write safety.
- No schema migrations.
- No query indexes.
- No multi-user ownership model.

Recommended migration path:

- SQLite for local-first desktop/mobile development.
- A repository/service abstraction around persistence before adding multiple clients.
- Explicit migrations for nudge notification fields and future extraction metadata.

### 5.5 Experimental MCP/RAG Path Still Has Production-Like Surface Area

`mcp_api_bridge.py`, `mcp_server.py`, `ragsystem/`, and Google sync utilities remain valuable experiments, but they are not part of the canonical MVP loop. They use broad CORS, provider tokens, and local synced data. They should not be presented as production-ready.

Recommended mitigation:

- Keep experimental pages visibly labeled.
- Avoid demoing real synced personal data.
- Gate experimental APIs behind explicit local-only flags if the app is ever hosted.

### 5.6 Documentation Drift

Several existing docs still describe AI extraction, notifications, or local automation as future work. The deep audit supersedes older statements. Follow-up doc synchronization should update roadmap, walkthrough, and implementation plan language so public claims match the actual code.

## 6. Flutter Migration Readiness Score

Overall score: 7.5 / 10

NudgeAI is moderately well prepared for a Flutter client because most core behavior is available through stateless REST endpoints and local JSON-backed backend state. The frontend does not own nudge persistence, context-rule math, extraction validation, or notification eligibility. This separation is the right direction for a future native client.

### Strengths

- REST endpoints are straightforward to call from Flutter:
  - `GET /api/nudges`
  - `POST /api/nudges`
  - `PATCH /api/nudges/{id}`
  - `POST /api/extract`
  - `POST /api/context-rules/evaluate`
  - `GET /api/notifications/poll`
- Notification eligibility is backend-owned and UI-agnostic.
- Alert payloads are raw JSON, not browser-specific objects.
- Context-rule evaluation does not depend on React internals.
- AI extraction returns structured suggestions that a mobile review screen can render directly.
- Local-first storage paths map conceptually to mobile on-device storage.

### Gaps Before Flutter

- Browser geolocation calls must be replaced with Flutter location permission APIs.
- Web Notification API dispatch must be replaced with native local notifications.
- Background polling must be adapted to iOS/Android background execution limits.
- Local backend hosting strategy must be clarified: embedded local server, IPC bridge, or direct Dart persistence/services.
- Auth/user identity remains absent.
- JSON persistence should be abstracted before introducing mobile clients.
- API response schemas should be formalized, ideally through OpenAPI generation or shared contracts.

### Migration Recommendation

The best Flutter migration path is not to port `Dashboard.jsx` directly. Instead:

1. Preserve the REST API contracts in `simple_api_server.py` as the behavioral reference.
2. Extract persistence and domain logic behind service boundaries.
3. Decide whether Flutter runs against a local FastAPI sidecar, a local SQLite-backed Dart service, or a hosted API.
4. Reuse `GET /api/notifications/poll` semantics for native local notifications.
5. Reuse `POST /api/extract` semantics for mobile review flows.

## Final Assessment

NudgeAI now has a credible local-first architecture for personal nudges. The project has evolved beyond static dashboard visualization into an active local assistant loop: create nudges, evaluate local context, extract suggestions from messy text, and emit desktop notifications without cloud push infrastructure.

The primary engineering trade-off is deliberate locality over production readiness. Local JSON files, permissive CORS, absence of auth, and experimental MCP/RAG surfaces are acceptable for a local prototype but must be addressed before deployment or multi-user use.

The immediate next hardening priorities are:

1. Split frontend bundles and lazy-load experimental routes.
2. Add a settings surface for polling intervals, timezone, and notification privacy.
3. Decide whether extraction review drafts should remain intentionally volatile or become local persisted sessions.
4. Introduce SQLite or a persistence abstraction before mobile migration.
5. Continue enforcing privacy guard checks before every commit or PR.
