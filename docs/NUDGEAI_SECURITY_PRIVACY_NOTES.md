# NudgeAI Security and Privacy Notes

## Current Security Posture

The repository is not production-ready from a security or privacy perspective. It is a prototype with open CORS in multiple FastAPI servers, no app-level authentication, OAuth helper scripts for Google tokens, committed sample/generated data and logs, and multiple unclear backend entry points. The frontend stores a possible `mcp_token` from localStorage, but no real auth flow was found.

## Data Handled

- user profile
- tasks/nudges
- notes
- calendar events
- documents and document metadata
- location history
- fitness/activity data
- contacts, if added later
- reminders
- AI prompts/outputs
- integration tokens
- logs and sync outputs

## Risks

| Risk | Severity | Current Evidence | Recommendation |
|---|---|---|---|
| No app authentication | High | No user/session model found. | Add auth before deploying user data. For local demo, label as single-user local mode. |
| Open CORS | High | `allow_origins=["*"]` in several API files. | Restrict origins per environment. |
| Personal data in repo files | High | Calendar/location/fit JSON and logs are committed-style files. | Audit, sanitize, or move to ignored demo fixtures. |
| Tracked private artifacts | High | Verification cleanup identified `api/env.local`, `calendar_events.json`, and three `data_sync/*.json` outputs as forbidden tracked artifacts. Current privacy guard should pass only when they are untracked. | Keep them ignored locally and rotate exposed credentials if they were ever committed or pushed. |
| Token file exposure | High | OAuth scripts create `token.json` and `drive_token.json`; ignored but mounted in Docker. | Keep tokens outside repo and document local-only storage. |
| AI prompt privacy | High | MCP/Hugging Face flow can send personal context externally. | Add explicit privacy note and provider controls. |
| Endpoint confusion | Medium | Multiple APIs/bridges with different contracts. | Consolidate to one backend and one API contract. |
| Silent mock fallback | Medium | Frontend/API often returns mock data after failures. | Label sample data clearly and surface errors. |
| Broken deployment path | Medium | `mcp_api_bridge.py` syntax error, Docker health mismatch. | Fix before public demo/deploy. |
| Sensitive logs | Medium | `logs/` and `*.log` exist in repo. | Do not log full personal content; ignore runtime logs. |
| Unvalidated AI output | Medium | Prompt outputs are not schema-bound in core UI. | Validate AI JSON before displaying/saving. |

## Minimum MVP Security Requirements

- no secrets committed
- env vars documented
- auth required for user data, unless explicitly local-only demo
- user-level access control before multi-user deployment
- input validation
- AI output validation
- logging avoids sensitive content
- CORS controlled
- rate limits for AI/API endpoints
- privacy note in README/docs
- demo data clearly separated from real user data

## AI Privacy Notes

If external AI APIs are used, pasted notes, calendar context, document metadata, location context, and generated outputs may leave the local machine. The app must disclose which provider is used, what data is sent, whether data is retained by the provider, and how users can disable AI processing. AI extraction should be optional; manual nudge creation should work without any external provider.

## Availability And Booking Privacy Notes

Availability features must not expose private calendar event titles, attendees, locations, descriptions, or meeting links. Free/busy ranges are safer than full calendar details, but they are still personal schedule data and should be shared only through user-selected availability windows.

Booking requests require anti-spam controls before any public link is deployed. Calendar event creation must require explicit user consent and clearly documented OAuth scopes.

## Health And Location Privacy Notes

Health data is sensitive personal data and should not be required for the core product. Google Fit should not be treated as a stable long-term integration until the future health data direction is confirmed, likely through Health Connect research.

Location data is highly sensitive because it can reveal home, work, routines, relationships, and habits. Location history should remain local-only/manual import until a production privacy design covers consent, retention, deletion, filtering, and redaction.

Current browser geolocation support is opt-in, runs only while the dashboard is open, and writes to ignored local JSON. It is not background mobile tracking and must not be represented as production location history.

## Personal Context Rules Privacy Notes

Places, current location, rule state, and personal nudges are private local data. Real coordinates should live only in ignored local files such as `data/places.json`, `data/current_location.json`, and `data/rule_state.json`.

Checked-in context demos must use sanitized sample coordinates only. The current Gym demo uses Sydney CBD sample coordinates and must not be replaced with private home, gym, work, or routine locations.

## Real Google Data Warning

The repository can now fetch and serve real Google Calendar and Drive metadata locally. This increases the privacy risk.

Real synced files may include sensitive personal or professional metadata. These files must be treated as private local artifacts, not demo-safe fixtures.

Sensitive generated files may include:

- `api/env.local`
- `calendar_events.json`
- `drive_documents.json`
- `drive_documents_rag.json`
- `data_sync/calendar_sync.json`
- `data_sync/drive_sync.json`
- `data_sync/sync_summary.json`

Current expected cleanup status: `api/env.local`, `calendar_events.json`, `data_sync/calendar_sync.json`, `data_sync/drive_sync.json`, and `data_sync/sync_summary.json` must be absent from `git ls-files` before commit. `python scripts/privacy_check.py` should pass before any PR.

Before any commit or PR, inspect whether these files contain real personal data. Prefer sanitized fixtures under a clearly named demo directory.

Sanitized public-demo fixtures live in `data/demo/`:

- `data/demo/calendar_events.demo.json`
- `data/demo/drive_documents.demo.json`
- `data/demo/nudges.demo.json`

These fixtures should stay fake and should not copy real event titles, file IDs, emails, names, locations, or meeting links.

## Secret Rotation Requirement

If `api/env.local`, OAuth tokens, provider keys, or Google API credentials were ever committed or exposed in git history, rotate them immediately.

Removing the file from the latest commit is not enough if the secret exists in history.

Use the local privacy check before committing:

```bash
python scripts/privacy_check.py
```

If the script reports tracked private artifacts, remove them from the git index and rotate any exposed credentials or OAuth tokens:

```bash
git rm --cached api/env.local
git rm --cached calendar_events.json
git rm --cached data_sync/calendar_sync.json
git rm --cached data_sync/drive_sync.json
git rm --cached data_sync/sync_summary.json
```

## Local-Only Google Sync Position

Google sync is currently local-only and experimental. It is not production-authenticated, not multi-user isolated, and not ready for hosted deployment.

## Current MVP Privacy Position

The manual nudge MVP can run without sending data to external AI providers.

Manual nudge data is stored locally in `data/nudges.json`.

Experimental Google sync data is separate from the core MVP and should be treated as private local data.

## Production Readiness Warning

Before production use, NudgeAI needs authentication, access control, a privacy policy, controlled CORS, tested deployment config, secure token storage, retention/deletion controls, sanitized logs, AI output validation, and automated tests. The current repository should be treated as a local prototype and planning foundation, not a production app.
