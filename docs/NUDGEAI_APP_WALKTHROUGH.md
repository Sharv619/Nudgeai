# NudgeAI App Walkthrough

## Current App Shape

NudgeAI is a private local-first personal nudge assistant. The core product is still the manual nudge lifecycle: create, view, snooze, dismiss, complete, and delete nudges.

The first context-aware layer is the local Gym Opportunity rule:

1. Set a demo/manual current location.
2. Set manual calendar availability in minutes.
3. Click `Check Context Rules Now`.
4. If the rule matches, NudgeAI creates a normal nudge.
5. If the rule is still cooling down, NudgeAI does not duplicate the nudge.

## Dashboard Sections

### Manual Nudges

Use the nudge form to create normal nudges. Smart triggers should also create normal nudges so they can use the same dashboard, status, snooze, dismiss, complete, and delete flow.

### Context Sources

The dashboard shows source status cards for:

- Location
- Calendar

Current statuses are local/demo only. There is no background mobile tracking and no production Google Calendar integration in this MVP.

### Local Automation

The dashboard has disabled-by-default local automation controls:

- `Use Browser Location Once` asks the browser for the current location and saves it to the local current-location store.
- `Poll browser location every 60s` repeats that browser geolocation request while the dashboard stays open.
- `Poll context rules every 60s` calls the local rule evaluator while the dashboard stays open.

These loops are client-side only. They stop when the dashboard unmounts or the tab closes. They do not perform background mobile tracking and do not upload coordinates to a cloud service.

### Manual Location Debug

Use:

- `Use Demo Gym Location` to put the current location inside the demo gym radius.
- `Use Far Away Demo` to test the non-match path.
- Manual latitude/longitude fields for local testing.

Private real coordinates should stay in ignored local files and should not be committed.

### Context Rule Evaluation

`Check Context Rules Now` evaluates the local rule engine. The first seeded rule is `Gym Opportunity`.

The success case is:

```text
demo/manual location near gym
calendar free for 45+ minutes
current time inside 06:00-22:00
cooldown expired
-> normal nudge created
```

### Place And Rule Editing

The dashboard includes edit modals for local places and context rules. Users can update:

- place name, coordinates, radius, tags, and enabled state
- rule place, required free minutes, time window, cooldown, enabled state, and nudge template

Edits call the local FastAPI API and persist to ignored local JSON files. Real coordinates should not be copied into checked-in demo fixtures.

## Not Implemented Yet

- Background mobile location
- Mobile push notifications
- Production Google Calendar OAuth/free-busy
- Health/Fit integration
- AI extraction
- Gmail
- Booking/public sharing
- Auth
- RAG/MCP expansion
