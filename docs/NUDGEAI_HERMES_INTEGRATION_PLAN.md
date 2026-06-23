# NudgeAI Hermes Integration Plan

## Summary

Hermes Agent should be treated as an optional self-hosted companion around NudgeAI, not as a required dependency for the current MVP. NudgeAI's canonical runtime remains the React/Vite frontend and `simple_api_server.py` FastAPI backend with local JSON persistence.

The first integration step is documentation and operating guidance: define how Hermes could help run, maintain, and extend a local NudgeAI installation without giving it unreviewed write access to personal data or changing the core nudge lifecycle.

## Integration Positioning

Hermes is a candidate local agent layer for:

- Scheduled reviews of local nudges, context rules, and source status.
- Local deployment maintenance such as health checks, backups, update reminders, and test runs.
- Drafting reusable skills or workflows after solving repeated NudgeAI setup or operations tasks.
- Optional multi-platform delivery experiments after NudgeAI has explicit consent, auth, and retention rules.

Hermes is not part of the V1 runtime path:

- Do not require Hermes to run the NudgeAI dashboard.
- Do not route core nudge CRUD through Hermes.
- Do not let Hermes directly mutate `data/*.json` stores as the default integration.
- Do not add autonomous messaging, scheduling, or external actions without review gates.

## Safe V1 Use Cases

### 1. Local Operations Assistant

Hermes can help a user operate the local prototype by running documented commands and reporting results:

- Start or check the backend and frontend.
- Run privacy checks before commits.
- Run backend tests and frontend builds.
- Remind the user to back up local JSON stores.
- Summarize known limitations before demo or deployment work.

Acceptance criteria:

- NudgeAI still runs without Hermes.
- Hermes actions are based on documented commands in `README.md`.
- Any command that could expose or alter personal data requires explicit user review.

### 2. Scheduled Nudge Review

Hermes can periodically inspect NudgeAI through future narrow APIs or reviewed scripts and prepare summaries such as:

- Overdue nudges.
- Due-today nudges.
- Snoozed nudges returning soon.
- Context rules that recently matched.
- Source status warnings for location or calendar abstractions.

Acceptance criteria:

- V1 remains read-only unless the user explicitly approves an action.
- Summaries avoid dumping full private note, calendar, Drive, location, or fitness contents.
- Any future API access uses the same auth and consent model as the rest of NudgeAI.

### 3. Skill Drafting

Hermes can draft reusable local skills for repeated NudgeAI workflows, such as:

- Running the local dev environment.
- Preparing a demo with sanitized fixtures.
- Checking whether private sync artifacts are tracked.
- Exporting a high-level nudge summary.

Acceptance criteria:

- Skills document workflows rather than silently changing NudgeAI behavior.
- Skills must not include secrets, OAuth tokens, personal calendar data, or real location data.
- Skills that write data must use reviewed commands or future official APIs.

## Deferred Runtime Bridge

A deeper Hermes bridge should wait until NudgeAI has a stable privacy and auth model. If added later, the bridge should be narrow and explicit:

- Prefer API calls over direct JSON file edits.
- Use least-privilege scopes such as read-only summaries before write actions.
- Log action metadata without logging full sensitive contents.
- Require confirmation before creating, editing, deleting, snoozing, or messaging about nudges.
- Keep manual nudge CRUD functional when Hermes is not installed or offline.

Potential future API surface:

- `GET /api/nudges?status=...` for read-only summaries.
- `POST /api/nudges` for explicitly confirmed nudge creation.
- `POST /api/context-rules/evaluate` for explicitly triggered local rule checks.
- A future audit endpoint for recent local actions, if NudgeAI adds an activity log.

## Verification Gate

Before adding Hermes claims to the public UI or marketing copy, verify the following from official sources:

- Official repository URL.
- Install command.
- License.
- Platform support.
- Supported messaging gateways.
- Security and telemetry claims.
- Whether the supplied Hermes copy is approved for use in NudgeAI.

Until verified, treat Hermes content as draft integration research rather than public product copy.

## Privacy And Security Rules

NudgeAI handles sensitive personal context. Any Hermes integration must follow the existing security posture in `README.md` and `docs/NUDGEAI_SECURITY_PRIVACY_NOTES.md`:

- Do not commit token files, local env files, private sync outputs, or generated data from real accounts.
- Use sanitized fixtures in `data/demo/` for demos.
- Avoid logging full note text, calendar event titles, Drive document names, location traces, or health data.
- Keep user review in front of every external message, file mutation, and long-running automation.
- Add production auth and consent controls before any hosted or remote Hermes workflow.

## Testing And Acceptance

Documentation-only V1 is complete when:

- This plan exists as a standalone doc.
- No frontend route, backend endpoint, dependency, or data store behavior changes.
- `README.md` still describes NudgeAI as runnable with `python simple_api_server.py` and `npm run dev`.
- The plan clearly marks Hermes as optional and unverified until official source checks are done.

Future bridge implementation should include:

- Backend tests for any new API access.
- Frontend tests or build verification for any UI affordance.
- Privacy guard updates if new local files, logs, or exports are introduced.
- Failure-path checks proving NudgeAI still works when Hermes is absent.

## Assumptions

- NudgeAI remains a local-first single-user MVP for now.
- Hermes is being evaluated as a self-hosted companion, not a replacement backend.
- The pasted Hermes content is draft material until verified.
- Background automation and multi-platform delivery are future work, gated by auth, consent, retention, and review UX.
    