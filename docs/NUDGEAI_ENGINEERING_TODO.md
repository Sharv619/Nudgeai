# NudgeAI Engineering TODO

## P0 - Must Fix Before Demo

Verification update from June 18, 2026: Python syntax checks, backend nudge/context tests, privacy guard, and frontend production build passed locally. CI now mirrors the same verification pipeline.

| Task | Area | Why It Matters | Suggested Files | Acceptance Criteria |
|---|---|---|---|---|
| Keep frontend build passing | Frontend | Manual verification shows `npm run build` passes; keep this as a release gate. | `frontend/package.json`, `frontend/package-lock.json` | `npm ci` then `npm run build` succeeds locally and in CI. |
| Keep MCP API bridge syntax-valid | Backend | Manual verification shows `mcp_api_bridge.py` compiles; keep it gated while backend entry points are consolidated. | `mcp_api_bridge.py` | `python -m py_compile mcp_api_bridge.py` passes. |
| Choose canonical backend entry point | Architecture | Current frontend/Docker/API files disagree on server and endpoints. | `simple_api_server.py`, `mcp_api_bridge.py`, `backend_data_api.py`, `nudgeai_data_api.py`, `frontend/vite.config.js`, Docker files | README names one backend; frontend proxy and Docker point to it. |
| Track root README intentionally | Documentation | `README.md` now exists but is still untracked in the current worktree. | `README.md`, `.gitignore` | README is added to git and setup path is clear. |
| Document environment variables | Config | `.env.example` is incomplete compared with scripts/docs. | `.env.example`, `README.md` | Required vs optional vars are listed with purpose and default behavior. |
| Define persisted nudge data model | Data model | No `Nudge` source of truth exists. | Backend app module, DB/schema file | Model includes id, title, context, due date, priority, status, created/updated/completed timestamps. |
| Keep manual nudge CRUD tested | Core product | Manual verification shows create/list/update/delete API tests pass. | Backend API, frontend nudge pages/components | Create/list/update/delete or archive works and persists. |
| Replace fake log/status claims in demo path | UX/trust | `DataLogs.jsx` shows synthetic production-like data. | `frontend/src/pages/DataLogs.jsx` | UI labels demo/sample logs clearly or hides page from MVP demo. |
| Keep minimum tests for core app passing | Testing | `tests.test_nudge_store` and `tests.test_nudge_api` passed manually. | `tests/`, frontend test setup | CRUD/API tests pass in one command. |
| Keep CI build gate passing | CI | Broken builds should be caught before demo. | `.github/workflows/ci.yml` | CI runs Python syntax/tests, privacy guard, and frontend build. |
| Keep private artifacts out of git index | Security/privacy | `api/env.local`, `calendar_events.json`, and three `data_sync/*.json` files were identified as private artifacts. | `.gitignore`, git index | `git ls-files` returns nothing for every private artifact. |
| Rotate exposed secrets/tokens if tracked | Security | Secrets in git history should be considered compromised. | Google Cloud / API providers | New credentials issued; old credentials revoked. |
| Keep real synced data files ignored | Privacy | Calendar/Drive metadata may be sensitive and current tracked copies must be removed from git. | JSON sync outputs, README | Real data is ignored and sanitized fixtures are used for demos. |
| Keep sanitized demo fixtures | Demo/privacy | Portfolio demos need safe data. | `data/demo/` | `calendar_events.demo.json`, `drive_documents.demo.json`, and `nudges.demo.json` exist. |
| Run privacy guard before PR | Security/privacy | Private sync outputs can reappear locally. | `scripts/privacy_check.py` | `python scripts/privacy_check.py` exits zero before commit/PR. |
| Add source status cards | UX/privacy | Calendar, Drive, health, and location states should be explicit instead of silently blank or mocked. | `frontend/src/pages/Dashboard.jsx`, data source docs | UI can show connected, demo fixture, missing credentials, manual import required, unsupported/deprecated, and error states. |
| Keep next-phase docs current | Documentation | Booking, health, and location plans should not drift into overclaims. | `docs/NUDGEAI_NEXT_PHASE_PRD.md`, context docs | Docs state that booking/context work is planning-only until implemented. |
| Keep context rules local-first | Personal context | Real coordinates and rule state are sensitive. | `.gitignore`, `data/demo/`, context API | Local data files are ignored; demo fixtures are sanitized. |

## P1 - Core MVP

| Task | Area | Why It Matters | Suggested Files | Acceptance Criteria |
|---|---|---|---|---|
| Build nudge dashboard | Frontend | Dashboard should show nudges, not only data sources. | `frontend/src/pages/Dashboard.jsx`, new nudge components | Pending, due today, overdue, snoozed, completed sections render. |
| Add nudge creation form | Frontend | Manual capture is the core loop. | New/create page or dashboard panel | Validation, loading, error, empty states are present. |
| Add status actions | Frontend/API | Users need complete/snooze/dismiss controls. | Nudge API and UI components | Status changes persist and update counts. |
| Create AI extraction service | AI/backend | AI should return structured suggestions, not free text only. | New service module; existing `mcp_server.py` can inspire prompts | Messy note returns validated JSON suggestions with confidence and reason. |
| Add AI review UI | Frontend | Users must control what gets saved. | New AI extraction component | Edit/discard/save per suggestion. |
| Add due/overdue computation | Backend/frontend | Reminders depend on reliable timing. | Nudge model/API/UI | Overdue state is deterministic and tested. |
| Add API error handling | Backend/frontend | Current UI often falls back to mock data silently. | `frontend/src/utils/api.js`, API routes | Failures are visible and do not masquerade as real data. |
| Seed demo data intentionally | Demo | Demo should be repeatable without personal data. | `data/demo/` or backend seed script | Seed command creates 5 realistic sample nudges. |
| Define availability model | Booking | Booking should start as user-controlled manual availability, not a full scheduling SaaS. | Future availability model/API docs | Availability windows can be represented without Google OAuth. |
| Convert booking request to nudge | Booking/core | Booking creates a commitment and should enter the nudge lifecycle first. | Future booking API, nudge API | A request can create an approval nudge before any calendar event exists. |
| Create sanitized booking demo | Demo/privacy | Portfolio booking demo should avoid private calendar data. | `data/demo/`, demo docs | Demo booking request uses fake names, times, and meeting details. |
| Keep context rule editor safe | Personal context | Places and rules should be editable without touching JSON manually. | Dashboard/settings UI, context API | User can edit place radius, free minutes, time window, and cooldown locally. |
| Keep browser geolocation and polling opt-in | Personal context | Browser location and rule polling are useful only if visible and user-controlled. | Dashboard context section | Browser location and rule polling are disabled by default, page-scoped, and never background-tracked. |

## P2 - Polish

| Task | Area | Why It Matters | Suggested Files | Acceptance Criteria |
|---|---|---|---|---|
| Add screenshots after app is real | Portfolio | Screenshots should reflect working features. | `docs/`, README | Screenshots are current and not fake. |
| Add architecture diagram image or Mermaid | Docs | Helps reviewers understand app quickly. | `docs/NUDGEAI_ARCHITECTURE.md` | Diagram matches canonical implementation. |
| Add settings page | UX | Timezone/reminder preferences affect due times. | New settings route | Preferences persist. |
| Add accessibility pass | Frontend | Demo and product should be usable. | Frontend components | Keyboard navigation and form labels work. |
| Consolidate legacy scripts | Maintenance | Root is crowded with backups/temp/demo scripts. | Root scripts/docs | Legacy files are moved or marked without deleting useful history. |
| Plan Google Calendar free/busy | Calendar/privacy | Free/busy is safer than exposing full event details. | Future calendar service docs | Only busy ranges are used for availability planning. |
| Plan approved event creation | Calendar/privacy | Event creation must require explicit user consent. | Future calendar service docs | No event is created without approval. |
| Research Health Connect | Health | Google Fit may not be reliable as a long-term data source. | Research docs | Health direction is documented before implementation. |
| Design local location import UX | Location/privacy | Location history is highly sensitive and may require manual export/import. | Future import UI docs | Raw location files remain local and ignored. |

## P3 - Later

| Task | Area | Why It Matters | Suggested Files | Acceptance Criteria |
|---|---|---|---|---|
| Calendar import to candidate nudges | Integration | Existing calendar ingestion can become useful after core loop. | `data_ingestion/calendar`, nudge import service | Calendar items can create reviewable suggestions. |
| Email follow-up detection | Integration | Important future value but high privacy/risk. | New integration module | Email suggestions are source-labeled and review-only. |
| Contact model | Product | Needed for relationship reminders. | DB schema/API/UI | Contacts link to nudges. |
| Proactive scoring | AI | Helps prioritize but should follow reliable CRUD. | AI service | Scores are explainable and user-adjustable. |
| Browser/email notifications | Notifications | Makes nudges resurface outside dashboard. | Scheduler/notification service | User can opt in/out and receive test notification. |
