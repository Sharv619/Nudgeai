# NudgeAI

## What It Is

NudgeAI is a local prototype/MVP foundation for turning scattered obligations into clear manual nudges that can be created, tracked, completed, snoozed, dismissed, and reopened.

## Current Status

Local prototype / MVP foundation. Not production-ready.

The canonical MVP backend is `simple_api_server.py` on port `8001`. Existing MCP, RAG, Google data, and bridge files remain in the repository as experimental/legacy prototype work, but they are not required for the core manual nudge loop.

## Core MVP

- Manual nudge creation
- Nudge dashboard
- Pending, due today, overdue, snoozed, completed, and dismissed sections
- Complete, snooze, dismiss, reopen, and delete actions
- JSON-file persistence for local demo use
- Local-first personal context rules
- Demo/manual Gym Opportunity rule
- Location and Calendar source status cards
- No AI keys required for the core MVP

## Tech Stack

- Frontend: React, Vite, Tailwind CSS
- Backend: FastAPI
- Persistence: local JSON file at `data/nudges.json`
- Experimental/future: MCP, RAG, Hugging Face, Google APIs, WhiteCircle

## Start Here / Local Integration

For the step-by-step local setup, run commands, API integration surface, and Hermes/MCP guidance, use:

```txt
docs/LOCAL_INTEGRATION_RUNBOOK.md
```

Recommended path:

1. Run the canonical backend: `python simple_api_server.py`.
2. Run the frontend from `frontend/`: `npm run dev`.
3. Open `http://localhost:3000`.
4. Integrate other local tools through the FastAPI endpoints, not by directly editing `data/*.json`.
5. Treat MCP, RAG, Google sync, and bridge files as experimental until the manual nudge loop is verified.

## Local Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

## Environment Variables

The manual nudge MVP does not require AI or Google credentials.

Optional variables:

- `NUDGE_STORE_PATH`: override local nudge store path. Defaults to `data/nudges.json`.
- `PLACES_STORE_PATH`: override local places store path. Defaults to `data/places.json`.
- `CONTEXT_RULES_STORE_PATH`: override local context rules store path. Defaults to `data/context_rules.json`.
- `RULE_STATE_STORE_PATH`: override local context rule state store path. Defaults to `data/rule_state.json`.
- `CURRENT_LOCATION_STORE_PATH`: override local current location store path. Defaults to `data/current_location.json`.
- `CALENDAR_AVAILABILITY_STORE_PATH`: override local free/busy abstraction store path. Defaults to `data/calendar_availability.json`.
- `VITE_USE_MOCK_DATA` / `REACT_APP_USE_MOCK_DATA`: optional frontend mock-data flags. The core dashboard should use the real local API by default.
- `HF_token`, `HF_MODEL`, `WHITECIRCLE_API_KEY`: used only by experimental AI/MCP/RAG paths.
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `GOOGLE_TOKEN`, `GOOGLE_APPLICATION_CREDENTIALS`: used only by experimental local Google sync/OAuth helpers.
- `MCP_SERVER_HOST`, `MCP_SERVER_PORT`: used only by experimental Docker/MCP bridge paths.
- `ELEVENLABS_API_KEY`, `GOOGLE_TTS_API_KEY`: used only by optional demo asset generation scripts.
- `LOG_LEVEL`: optional logging control.

Google OAuth token files such as `token.json` and `drive_token.json` must not be committed.

## Secret Handling

Never commit:

- `api/env.local`
- `.env`
- `*.env.local`
- `token.json`
- `drive_token.json`
- OAuth credentials
- Google API tokens
- generated files containing real personal Calendar or Drive data

Check whether sensitive files are tracked:

```bash
git ls-files api/env.local
git ls-files token.json
git ls-files "*.env.local"
git ls-files calendar_events.json
git ls-files data_sync/calendar_sync.json
git ls-files data_sync/drive_sync.json
git ls-files data_sync/sync_summary.json
```

Historical verification cleanup finding: `api/env.local`, `calendar_events.json`, `data_sync/calendar_sync.json`, `data_sync/drive_sync.json`, and `data_sync/sync_summary.json` were identified as private artifacts that must stay out of git tracking.

Remove tracked private artifacts without deleting local files:

```bash
git rm --cached api/env.local
git rm --cached calendar_events.json
git rm --cached data_sync/calendar_sync.json
git rm --cached data_sync/drive_sync.json
git rm --cached data_sync/sync_summary.json
```

If these files are already untracked, do not re-add them. Rotate any exposed keys/tokens if they were ever committed or pushed. Removing a file from the latest commit is not enough if the secret exists in git history. If any real Google OAuth tokens, API keys, or provider credentials were ever committed, treat them as compromised.

Run the local privacy guard before committing:

```bash
python scripts/privacy_check.py
python scripts/nudgeai_health_check.py
```

The script fails if private Google sync outputs, OAuth tokens, or local env files are tracked by git. It warns, but does not fail, when those files merely exist locally and are ignored.

## Run Commands

Backend:

```bash
python simple_api_server.py
```

Frontend:

```bash
cd frontend
npm run dev
```

Open the frontend at `http://localhost:3000`. The Vite dev server proxies `/api` to `http://localhost:8001`.

## Test / Verification Commands

Backend syntax:

```bash
python -m py_compile simple_api_server.py mcp_api_bridge.py
```

Backend store tests:

```bash
python -m unittest discover -s tests -p "test_nudge*.py"
```

Frontend build:

```bash
cd frontend
npm ci
npm run build
```

## Nudge API

- `GET /api/nudges`
- `GET /api/nudges/summary`
- `POST /api/nudges`
- `PATCH /api/nudges/{id}`
- `DELETE /api/nudges/{id}`

Supported filters on `GET /api/nudges`:

- `status`
- `priority`
- `dueToday`
- `overdue`

`DELETE` hard-deletes a local MVP nudge.

When a nudge is marked `completed`, `completedAt` is set. When a completed nudge is reopened or moved to another status, `completedAt` is cleared.

## Current Local Endpoints

Core nudge MVP:

- `GET /health`
- `GET /api/nudges`
- `POST /api/nudges`
- `PATCH /api/nudges/{id}`
- `DELETE /api/nudges/{id}`

Experimental Google data endpoints:

- `GET /api/mcp/tools/query_calendar`
- `GET /api/mcp/tools/query_drive`

The Google endpoints are experimental, local-only, and not production integrations.

## Experimental Google Data Sync

NudgeAI includes experimental local Google Calendar and Google Drive sync utilities.

These utilities can fetch real local user data and serve it through local API endpoints:

- `GET /api/mcp/tools/query_calendar`
- `GET /api/mcp/tools/query_drive`

This is not part of the production MVP path yet. The core MVP remains the manual nudge lifecycle.

The Google sync path is local-only and should be treated as sensitive because it may include:

- calendar event titles
- event times
- meeting metadata
- Drive document names
- Drive document metadata
- file IDs or references
- generated sync summaries

Do not commit real synced Google data unless it has been explicitly sanitized.

## Sanitized Demo Fixtures

Public demos should use fake fixture data from `data/demo/`, not private synced Google files.

Current sanitized fixtures:

- `data/demo/calendar_events.demo.json`
- `data/demo/drive_documents.demo.json`
- `data/demo/nudges.demo.json`
- `data/demo/places.demo.json`
- `data/demo/context_rules.demo.json`
- `data/demo/current_location.demo.json`
- `data/demo/calendar_availability.demo.json`

These files use fake IDs, fake names, and demo-only metadata so they can support portfolio walkthroughs without exposing private Calendar or Drive data.

## Personal Context Rules

NudgeAI is pivoting toward private context-aware personal nudges, not booking SaaS. The first local rule is `Gym Opportunity`.

Current local/demo loop:

```text
manual/demo location + manual calendar free minutes + local rule
-> evaluate context
-> create a normal nudge when the rule matches
```

The dashboard supports Location and Calendar source status cards, demo gym/far-away location controls, and a `Check Context Rules Now` action. This is not live background location, production Google Calendar, Health/Fit, Gmail, AI extraction, auth, or booking.

## Planning Docs

- [Deep Audit](docs/NUDGEAI_DEEP_AUDIT.md)
- [PRD](docs/NUDGEAI_PRD.md)
- [Next Phase PRD](docs/NUDGEAI_NEXT_PHASE_PRD.md)
- [Focus Chain](docs/NUDGEAI_FOCUS_CHAIN.md)
- [Engineering TODO](docs/NUDGEAI_ENGINEERING_TODO.md)
- [Roadmap](docs/NUDGEAI_ROADMAP.md)
- [Architecture](docs/NUDGEAI_ARCHITECTURE.md)
- [Demo Plan](docs/NUDGEAI_DEMO_PLAN.md)
- [App Walkthrough](docs/NUDGEAI_APP_WALKTHROUGH.md)
- [Next Implementation Plan](docs/NUDGEAI_NEXT_IMPLEMENTATION_PLAN.md)
- [Local Automation](docs/NUDGEAI_LOCAL_AUTOMATION.md)
- [Security and Privacy Notes](docs/NUDGEAI_SECURITY_PRIVACY_NOTES.md)

## Next Phase Planning

The next phase focuses on personal context rules: places, manual/demo location, calendar free/busy abstraction, and normal nudge creation when a rule matches. Booking remains optional later work. The manual nudge MVP remains the core product path.

- [Next Phase PRD](docs/NUDGEAI_NEXT_PHASE_PRD.md)
- [Booking and Availability Plan](docs/NUDGEAI_BOOKING_AVAILABILITY_PLAN.md)
- [Context Sources Plan](docs/NUDGEAI_CONTEXT_SOURCES_PLAN.md)
- [Data Source Limitations](docs/NUDGEAI_DATA_SOURCE_LIMITATIONS.md)

## Known Limitations

- No production auth yet.
- No real notifications yet.
- AI extraction is not part of the core MVP yet.
- Google/MCP/RAG integrations are experimental/future paths.
- Local JSON persistence is suitable for demo/local development only.
- CORS is permissive for local development and must be locked down before deployment.
