# NudgeAI Next Implementation Plan

## Product Direction

NudgeAI is now focused on private context-aware personal nudges, not public booking or scheduling SaaS.

Core loop:

```text
my location + my calendar + my rules
-> detect useful moment
-> create/ping a nudge
-> I act, snooze, dismiss, or complete it
```

## Completed In This Sprint

- Local/demo places config.
- Local/demo context rules config.
- Manual/demo current location source.
- Calendar free/busy abstraction using free minutes, not event titles.
- Rule evaluator with distance, time window, calendar availability, and cooldown checks.
- First `Gym Opportunity` rule.
- Source status cards for Location and Calendar.
- Normal nudge creation when a rule matches.
- Backend tests for evaluator behavior.
- Backend `PATCH`/`PUT` endpoints for local places and context rules.
- Dashboard edit modals for places and context rules.
- Opt-in browser geolocation while the dashboard is open.
- Disabled-by-default context rule polling using frontend `setInterval`.
- CI workflow for syntax checks, backend tests, privacy guard, and frontend build.

## Next Sprint

1. Add a desktop/browser notification experiment after rule-created nudges are stable.
2. Add richer source status details without exposing private event titles.
3. Add explicit fixture loading/reset commands for public demos.
4. Add a small settings surface for local automation intervals and timezone.
5. Start AI extraction only after the automation and edit flows stay stable.

## Still Deferred

- AI extraction
- Gmail
- Auth
- Public booking
- Production Google Calendar OAuth
- Health/Fit
- Health Connect
- Background mobile tracking
- RAG/MCP expansion

## Privacy Requirement

Real coordinates, local rule state, current location, and personal nudges must stay in ignored local files. Browser geolocation is opt-in, page-scoped, and local-only. Public demos must use sanitized `data/demo/*.demo.json` fixtures.
