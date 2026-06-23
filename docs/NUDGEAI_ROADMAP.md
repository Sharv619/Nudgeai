# NudgeAI Roadmap

## V0: Repo Stabilisation

Goal:
Make the project understandable and runnable.

Deliverables:
- working local setup
- documented env vars
- build verified
- one canonical backend
- README updated
- audit docs complete
- fake production/demo claims removed or clearly labeled
- real Google sync data ignored or replaced with sanitized demo fixtures

## V1: Manual Nudge Stability

Goal:
Make the manual nudge lifecycle reliable enough to remain the product foundation.

Deliverables:
- stable manual nudge CRUD
- edit nudge flow
- status filters
- due/overdue behavior
- CI gate
- demo fixtures kept safe

## V1.5: Booking And Context Planning

Goal:
Plan the next phase without moving integrations ahead of core reliability.

Deliverables:
- booking/availability planning
- source status UX plan
- data source limitations docs
- privacy rules for availability, health, and location

## V2: AI-Assisted Nudge Creation

Goal:
AI turns messy notes into structured nudges after the manual loop is reliable.

Deliverables:
- messy note input
- nudge extraction
- suggested action
- confidence/reason
- human review
- fallback handling

## V3: Reminder System

Goal:
Nudges resurface at the right time.

Deliverables:
- scheduled reminders
- overdue state
- snooze scheduling
- daily digest
- notification mechanism

## V4: Calendar Booking Integration

Goal:
Availability and booking become calendar-backed only after consent and privacy controls are designed.

Deliverables:
- Google Calendar free/busy read
- booking request approval
- calendar event creation after approval
- prep/follow-up nudges

## V5: Health And Location Context Improvements

Goal:
Improve sensitive context sources without making them required.

Deliverables:
- Health Connect research
- Google Fit limitation handling
- location import UX
- local-only context handling
- source status cards

## V6: Proactive Relationship/Work Assistant

Goal:
High-signal proactive nudges.

Deliverables:
- relationship gap detection
- smart follow-up suggestions
- weekly review
- user preference learning
- explainable priority scoring

## Hermes Integration Track

Goal:
Use Hermes as an optional local operations and automation companion without making it required for the NudgeAI runtime.

Deliverables:
- H0 documentation-only integration and repo guardrails
- H1 local operations health checks
- H2 read-only nudge summary endpoint for safe daily reviews
- H3 reviewed nudge create/edit/delete actions through FastAPI only
- H4 optional MCP wrapper after API/privacy boundaries stabilize
- H5 optional gateway delivery after auth, audit, consent, and retention rules exist

Success Criteria:
- NudgeAI still runs without Hermes.
- Hermes never mutates `data/*.json` directly by default.
- Read-only summaries avoid raw Calendar, Drive, health, and location dumps.
- Any write action requires explicit user approval and auditability.

## Roadmap Table

| Version | Theme | Key Features | Success Criteria |
|---|---|---|---|
| V0 | Stabilise | Build, syntax, canonical API, docs, env vars | New developer can run app locally from README. |
| V1 | Manual stability | Edit, filters, due behavior, CI, demo fixtures | User can manage nudges reliably without AI. |
| V1.5 | Next-phase planning | Booking plan, source status UX, limitations docs | Future work is scoped before implementation. |
| V2 | AI assist | Messy note extraction, review, validated JSON | User saves useful suggestions after review. |
| V3 | Reminders | Scheduler, overdue, digest, notification | Nudges resurface without manually checking dashboard. |
| V4 | Calendar booking | Free/busy, approval, event creation | Booking is consent-based and does not leak private calendar details. |
| V5 | Health/location context | Health Connect research, local location import UX | Sensitive context remains optional and controlled. |
| V6 | Proactive assistant | Relationship/work intelligence, preferences | Assistant is high-signal and user-controlled. |
