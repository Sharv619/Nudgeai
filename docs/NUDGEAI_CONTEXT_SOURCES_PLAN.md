# NudgeAI Context Sources Plan

## Context Source Matrix

| Source | Current State | MVP Role | Privacy Risk | Next Step |
|---|---|---|---|---|
| Manual nudges | implemented | core | low/medium | improve UX |
| Sanitized demo fixtures | implemented | demo | low | keep |
| Google Calendar events | experimental local sync | future context | high | free/busy planning |
| Google Drive metadata | experimental local sync | future context | medium/high | keep local-only |
| Google Fit | unclear/legacy risk | not MVP | high | document limitation / Health Connect research |
| Browser geolocation | implemented opt-in while app is open | local context | high | keep page-scoped and user-controlled |
| Location history | manual/export-based | not MVP | very high | local import UX only |
| AI extraction | not implemented | V2 | medium/high | plan after manual loop |
| Gmail | not implemented | later | very high | defer |

## Manual Nudges

Manual nudges are the core product. They must work without integrations, AI keys, Google credentials, or external providers.

## Calendar

Calendar context is useful for availability, meeting prep, and follow-up nudges. The safer first planning step is free/busy availability, not full event metadata exposure. Full event creation should only happen after explicit user approval.

## Drive

Drive metadata can provide document context, but it is not core to the nudge MVP. Keep Drive sync local-only and avoid making Drive data part of the public demo path unless sanitized fixtures are used.

## Google Fit / Health

Google Fit dashboard data may not appear because data access depends on API setup, permissions, device/source availability, sync state, and the broader migration away from Google Fit APIs.

Do not make Google Fit central to NudgeAI. Create a future Health Connect research spike instead, and use demo fixtures for portfolio walkthroughs where health context needs to be illustrated.

## Location History

Location history is high-value but high-risk. Manual export/import may be required because Google Maps Timeline data is not a simple production-ready app integration.

The implemented browser geolocation control is not location history. It asks the browser for current coordinates while the dashboard is open and stores the result in the ignored local current-location file.

Recommended MVP handling:

- Support sanitized fixtures.
- Support local-only import.
- Show clear not connected status.
- Never commit raw location files.

## Data Source Status UX

Plan a dashboard section that can show:

- Connected
- Demo fixture
- Local file found
- Missing credentials
- Needs manual import
- Unsupported/deprecated
- Error loading

## Recommended Order

1. Manual nudges
2. Demo fixtures
3. Local places/rules and browser geolocation while open
4. Calendar free/busy
5. Booking request nudges
6. Health Connect research
7. Location import UX
8. Gmail later
