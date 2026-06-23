# NudgeAI Local Integration Runbook

This is the practical setup guide for running and integrating the local NudgeAI repo on Sharv619's machine.

## Repo Location

```txt
C:\Users\Hlade\Documents\nudgeAI\nudgeai
```

GitHub repo:

```txt
https://github.com/Sharv619/Nudgeai
```

## Recommended Integration Path

Use the local FastAPI + Vite path first. Treat MCP, RAG, Google sync, and bridge files as experimental until the core app is running cleanly.

Canonical local runtime:

- Backend: `simple_api_server.py`
- Backend port: `8001`
- Frontend: `frontend/`
- Frontend dev server: `http://localhost:3000`
- Frontend API proxy: `/api` -> `http://localhost:8001`
- Local persistence: JSON files under `data/`

## One-Time Setup

From PowerShell or a normal Windows terminal:

```powershell
cd C:\Users\Hlade\Documents\nudgeAI\nudgeai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install the frontend dependencies:

```powershell
cd C:\Users\Hlade\Documents\nudgeAI\nudgeai\frontend
npm install
```

Create a local environment file only if you need to override defaults:

```powershell
cd C:\Users\Hlade\Documents\nudgeAI\nudgeai
copy .env.example .env
```

Do not commit `.env`, token files, or generated personal data.

## Daily Local Startup

Terminal 1 — backend:

```powershell
cd C:\Users\Hlade\Documents\nudgeAI\nudgeai
.\.venv\Scripts\Activate.ps1
python simple_api_server.py
```

Backend health check:

```txt
http://localhost:8001/health
```

Terminal 2 — frontend:

```powershell
cd C:\Users\Hlade\Documents\nudgeAI\nudgeai\frontend
npm run dev
```

Open:

```txt
http://localhost:3000
```

## What To Integrate First

Start with the manual nudge MVP before deeper automation:

1. Create a manual nudge from the dashboard.
2. Confirm it appears in the pending list.
3. Mark it completed.
4. Reopen it.
5. Snooze it.
6. Delete it.
7. Check that `data/nudges.json` changes locally.

If this loop works, the core local integration is healthy.

## API Surface To Use From Other Local Tools

Use HTTP calls to `simple_api_server.py` instead of writing directly to JSON files.

Core endpoints:

```txt
GET    /health
GET    /api/nudges
GET    /api/nudges/summary
POST   /api/nudges
PATCH  /api/nudges/{id}
DELETE /api/nudges/{id}
GET    /api/context
GET    /api/source-status
POST   /api/extract
POST   /api/current-location
PATCH  /api/context/calendar
POST   /api/context-rules/evaluate
GET    /api/notifications/poll
```

Example nudge create request:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://localhost:8001/api/nudges `
  -ContentType 'application/json' `
  -Body '{"title":"Follow up with Priya","priority":"high"}'
```

Curl equivalent:

```bash
curl -X POST http://localhost:8001/api/nudges \
  -H "Content-Type: application/json" \
  -d '{"title":"Follow up with Priya","priority":"high"}'
```

## Optional Hermes/MCP Integration Guidance

For now, the safest Hermes integration is an operations assistant around the HTTP API:

- Start/check the backend and frontend.
- Run tests and privacy checks.
- Summarize due/overdue nudges through `GET /api/nudges`.
- Create/edit/delete nudges only after explicit user approval.

Do not make Hermes or any agent mutate `data/*.json` directly by default. Prefer the FastAPI endpoints so validation, timestamps, notification state, and future auth hooks remain centralized.

Experimental MCP files are present, but should be treated as future/legacy until the HTTP runtime is stable:

```txt
mcp_server.py
mcp_api_bridge.py
mcp_http_gateway.py
http_mcp_adapter.py
proper_mcp_http_bridge.py
```

## Optional Google Data Setup

Google Calendar/Drive/Fit/location integrations are experimental and sensitive. Only enable them after the local nudge MVP works.

Useful files/scripts:

```txt
setup_google_auth.py
run_google_auth.py
fetch_google_data.py
data_ingestion/calendar/fetch_calendar_events.py
data_ingestion/drive/fetch_drive_documents.py
data_ingestion/fit/fetch_fit_data.py
data_ingestion/location/fetch_location_history.py
```

Sensitive generated files must stay local and ignored:

```txt
token.json
drive_token.json
calendar_events.json
drive_documents.json
drive_documents_rag.json
data_sync/*.json
```

Use sanitized fixtures in `data/demo/` for demos.

## Verification Before Commit

Run these from the repo root:

```powershell
python -m py_compile simple_api_server.py mcp_api_bridge.py
python -m unittest discover -s tests -p "test_nudge*.py"
python scripts/privacy_check.py
python scripts/nudgeai_health_check.py
```

Frontend check:

```powershell
cd frontend
npm run build
```

## Troubleshooting

### Frontend cannot reach backend

Check:

1. `python simple_api_server.py` is running.
2. `http://localhost:8001/health` responds.
3. `frontend/vite.config.js` still proxies `/api` to `http://localhost:8001`.
4. Frontend was restarted after changing `.env` or Vite config.

### Backend dependency error

Re-activate the venv and reinstall:

```powershell
cd C:\Users\Hlade\Documents\nudgeAI\nudgeai
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Google auth/data issues

Do not debug with real data in git. Keep token files local, rerun the auth setup, and use demo fixtures for public demos.

### Privacy check fails

Remove tracked private artifacts without deleting local files:

```powershell
git rm --cached <path>
```

Then rotate any credentials or OAuth tokens that were committed or pushed.
