# NudgeAI Demo Plan

## Demo Goal

Show that NudgeAI helps users turn messy obligations into clear action nudges.

Current repo warning: the app is still a local prototype, but the manual nudge dashboard and local Gym Opportunity rule can now support an honest demo.

## 3-Minute Demo Script

Current manual nudge demo:

1. Open app.
2. Show the nudge dashboard.
3. Create a manual nudge.
4. Show pending/due/overdue/completed sections where available.
5. Complete/snooze one nudge.
6. Explain that AI extraction, reminders, booking, and production integrations are planned later.

Do not claim AI extraction, reminders, booking, or production integrations during the current demo.

## Future Demo Scripts

These flows are either local/demo-only or not implemented yet.

### Local Context Rule Demo

Implemented as a local/demo flow:

1. Open the dashboard.
2. Show Location and Calendar source status cards.
3. Click `Use Demo Gym Location`.
4. Set calendar free minutes to at least `45`.
5. Click `Save Context`.
6. Click `Check Context Rules Now`.
7. Show the `Gym opportunity` nudge in the normal nudge dashboard.
8. Click again and show that cooldown prevents duplicate nudges.
9. Optionally show the place/rule edit modals and explain that real coordinates stay local.
10. Optionally enable browser location or rule polling while emphasizing that both are opt-in and page-scoped.

### Future Booking Request Demo

1. User defines manual availability windows.
2. Visitor submits a meeting request.
3. Booking request appears as an approval nudge.
4. User approves or rejects.
5. Approved request later creates prep/follow-up nudges or a calendar event after consent.

### Future Context Source Status Demo

1. Dashboard shows Calendar, Drive, Health, and Location source status cards.
2. Calendar/Drive can show demo fixture or local-only status.
3. Health explains that Google Fit may be unavailable and needs future Health Connect research.
4. Location explains that manual export/import may be required.
5. Public demo uses sanitized fixtures only.

## Demo Dataset

## Experimental Google Data Demo Warning

The app can locally display real Google Calendar and Drive data if synced, but this should not be used in public demos unless the data is sanitized.

For public portfolio demos, use sanitized fixture data only.

Use the checked-in fixtures under `data/demo/` for public walkthroughs:

- `data/demo/calendar_events.demo.json`
- `data/demo/drive_documents.demo.json`
- `data/demo/nudges.demo.json`

Before recording or publishing a demo, run:

```bash
python scripts/privacy_check.py
```

Do not show root-level Google sync outputs or files from `data_sync/` unless they have been explicitly sanitized.

### 1. Follow-up after networking event

Sample input:
```text
Met Priya at the Sydney AI meetup. She said to send my portfolio and remind her about the agent demo next week.
```

Expected nudges:
- Send portfolio to Priya.
- Follow up about agent demo next week.

### 2. Job application follow-up

Sample input:
```text
Applied to Atlassian grad role on Monday. Recruiter said responses usually take 5 business days. Check in if I do not hear back.
```

Expected nudges:
- Check application response after 5 business days.
- Prepare short follow-up message.

### 3. Meeting prep

Sample input:
```text
Meeting with Manoj tomorrow night about project planning. Need to review notes, list blockers, and send agenda before the call.
```

Expected nudges:
- Review project notes before meeting.
- List current blockers.
- Send agenda to Manoj.

### 4. Invoice/payment reminder

Sample input:
```text
Client invoice was sent last Friday. Payment due in 7 days. If unpaid, send a polite reminder.
```

Expected nudges:
- Check invoice payment status.
- Send payment reminder if unpaid.

### 5. Personal admin task

Sample input:
```text
Room inspection is coming up. Need to clean kitchen, confirm time with Bish, and print the lease page.
```

Expected nudges:
- Clean kitchen before room inspection.
- Confirm inspection time with Bish.
- Print lease page.

## What To Say

NudgeAI is a personal productivity assistant focused on turning scattered obligations into clear, reviewable nudges. The current codebase already explores calendar, location, document, fitness, RAG, and MCP context. The next product step is to anchor that context around a simple nudge lifecycle: create, review, snooze, dismiss, and complete.

## What Not To Claim

- Do not claim production readiness.
- Do not claim real notifications until implemented.
- Do not claim persisted nudge management until implemented.
- Do not claim multi-user security.
- Do not claim email/calendar integrations are product-ready.
- Do not claim booking/availability is implemented until it is actually built.
- Do not claim background location is implemented.
- Do not claim production Google Calendar free/busy is implemented.
- Do not claim Google Fit is a stable future integration path.
- Do not claim automatic Google Maps Timeline ingestion is production-ready.
- Do not claim fake logs or mock metrics are live operational data.
- Do not claim AI outputs are reliable without validation and review.
- Do not claim production Google integration.
- Do not show private Calendar or Drive metadata in public demos.
- Do not claim synced data is safe to commit.
- Do not claim hosted multi-user Google auth.

## Known Limitations

- Frontend production build now passes in local verification.
- `mcp_api_bridge.py` now passes Python syntax verification.
- Manual nudge API/store tests now pass, but the public demo path still needs explicit fixture-loading/reset wiring.
- No app auth exists.
- Existing frontend falls back to mock data in several places.
- Legacy experimental data-dashboard pages still exist outside the core nudge path.
- Docker setup likely does not match the actual MCP HTTP behavior.
- Privacy guard should pass before any public demo or commit; local private artifacts may remain on disk only if ignored and untracked.
