# NudgeAI Local Automation

## Purpose

Local automation moves NudgeAI beyond a static manual MVP without changing the privacy model. It lets the browser provide current location while the dashboard is open and lets the dashboard poll local context rules on a visible, opt-in interval.

## Implemented Controls

- `Use Browser Location Once`: calls browser geolocation once and saves the result through `POST /api/current-location`.
- `Poll browser location every 60s`: repeats browser geolocation while the dashboard is open.
- `Poll context rules every 60s`: calls `POST /api/context-rules/evaluate` while the dashboard is open.
- Place edit modal: updates local place name, coordinates, radius, tags, and enabled state.
- Context rule edit modal: updates place selection, required free minutes, time window, cooldown, enabled state, and nudge template.

## API Endpoints

- `PATCH /api/places/{place_id}`
- `PUT /api/places/{place_id}`
- `PATCH /api/context-rules/{rule_id}`
- `PUT /api/context-rules/{rule_id}`
- `POST /api/current-location`
- `PATCH /api/context/calendar`
- `POST /api/context-rules/evaluate`

## Privacy Guardrails

- Automation is disabled by default.
- Browser geolocation is requested by the browser permission prompt.
- Polling runs only while the dashboard is open.
- No background mobile location tracking exists.
- Coordinates and rule state persist only to ignored local JSON files.
- Public demos must use sanitized fixtures under `data/demo/`.
- Do not copy real home, work, gym, or routine locations into checked-in fixtures.

## Current Limitations

- Poll intervals are fixed at 60 seconds in the frontend.
- There is no browser notification delivery yet.
- There is no production Google Calendar free/busy integration yet.
- There is no auth or multi-user isolation yet.
- Place/rule editing is local-first and intentionally simple.
