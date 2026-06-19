# NudgeAI Focus Chain

## Purpose

This document defines the build order for NudgeAI so development stays focused.

## Core Principle

Do not build integrations before the core nudge loop works.

Real Google Calendar/Drive sync is useful local proof, but it does not change the product order. Public portfolio proof should use sanitized fixtures, not private synced data.

Next-phase planning must preserve this order:

1. Manual nudge lifecycle
2. Demo-safe data and privacy guardrails
3. Personal context rules
4. AI extraction from messy notes
5. Reminder system
6. Calendar booking integration with user approval
7. Health/location context improvements
8. Proactive assistant later

## Focus Chain Overview

1. Product clarity
2. Repo stabilization
3. Canonical backend selection
4. Data model
5. Manual nudge creation
6. Nudge dashboard
7. Nudge status lifecycle
8. Demo-safe fixture data
9. CI/testing
10. Personal context rules
11. Context source status UX
12. AI extraction from messy notes
13. Reminder scheduling
14. Basic notification layer
15. Calendar booking integration with user approval
16. Health/location context improvements
17. Advanced proactive AI

## Phase 0: Stabilise the Repo

Goal:
Clean enough that the project can be understood and run.

Tasks:
- verify install
- verify frontend build
- verify Python entry points
- pick one canonical API
- document run instructions
- identify missing env vars
- remove or mark broken assumptions
- move fake logs/demo claims out of production-facing UI

Exit criteria:
- app can run locally
- README explains how
- audit docs exist
- `npm run build` works
- chosen backend imports cleanly

## Phase 1: Define the Product

Goal:
NudgeAI has one clear MVP direction.

Tasks:
- define target user
- define core nudge loop
- define MVP use cases
- define non-goals
- decide what existing RAG/MCP UI remains in MVP

Exit criteria:
- PRD complete
- MVP scope clear
- out-of-scope list clear

## Phase 2: Core Nudge Loop

Goal:
User can create, view, update, and complete nudges.

Tasks:
- create nudge
- list nudges
- update nudge status
- snooze/dismiss/complete
- persist nudges
- add empty, loading, error, and overdue states

Exit criteria:
- full manual nudge lifecycle works without AI keys

## Phase 3: AI Assist Layer

Booking planning can happen before this phase, but booking implementation should not distract from manual nudge reliability. Health/location work should stay behind context source status UX and privacy guardrails.

Goal:
AI helps create useful nudges from messy input.

Tasks:
- messy note input
- extract action items
- generate suggested nudges
- validate JSON
- confidence score
- user review before save
- fallback when AI fails
- do not save hallucinated or unreviewed suggestions

Exit criteria:
- AI suggestions are useful but not blindly trusted

## Phase 4: Reminders and Notifications

Goal:
Nudges actually resurface at the right time.

Tasks:
- due dates
- reminder time
- overdue state
- notification mechanism
- daily summary
- snooze scheduling

Exit criteria:
- user gets nudged without manually checking dashboard

## Phase 5: Demo Readiness

Goal:
The app can be shown to a recruiter/community stakeholder.

Tasks:
- clean README
- screenshots
- demo script
- seeded demo data
- architecture diagram
- known limitations section
- remove fake production metrics/log claims from the demo path

Exit criteria:
- 3-minute demo works reliably

## Phase 6: Personal Context Rules

Goal:
Build local-first personal context rules without implementing production integrations.

Tasks:
- define places
- define context rules
- add manual/demo current location
- add calendar free/busy abstraction
- create normal nudges on rule match
- keep rule state and real coordinates ignored

Exit criteria:
- Gym Opportunity can create a normal nudge
- second evaluation during cooldown does not duplicate
- no production Google, health, Gmail, auth, booking, or background tracking is added

## Phase 7: Integrations

Goal:
Connect external context sources only after core loop works.

Possible integrations:
- Google Calendar
- Gmail
- Contacts
- Notion
- Slack
- CRM

Exit criteria:
- integration creates useful candidate nudges without overwhelming user

## Phase 8: Proactive Assistant

Goal:
NudgeAI becomes proactive.

Tasks:
- meeting prep nudges
- follow-up detection
- relationship gap detection
- priority scoring
- weekly review
- preference learning

Exit criteria:
- assistant creates high-signal nudges with user control
