# NudgeAI Next Phase PRD

## 1. Purpose

This document defines the next product phase after the manual nudge MVP foundation. It keeps the current product centered on reliable manual nudges while planning private context-aware personal nudges.

## 2. Current Product Baseline

- Manual nudge CRUD works.
- Nudge data persists to local JSON.
- Privacy guardrails exist through `scripts/privacy_check.py`.
- Sanitized demo fixtures exist under `data/demo/`.
- Experimental Calendar and Drive data endpoints exist for local-only prototype use.
- Local place/rule editing exists for the first context rules.
- Browser geolocation can be fetched while the dashboard is open, with user opt-in.
- Context rule polling exists as a disabled-by-default dashboard loop.
- There is no production auth.
- There are no production integrations.
- AI extraction is not implemented yet.
- There is no real notification layer yet.

## 3. Next Phase Theme

From manual nudges to private context-aware personal support.

## 4. Problem Statements

### Problem A: Useful Moments Are Easy To Miss

Users want NudgeAI to notice when they are near an important place, free enough to act, and outside cooldown. The first example is a gym opportunity nudge.

### Problem B: Health/Activity Data Is Confusing And Unreliable

Google Fit data may not appear consistently because health data APIs, permissions, devices, provider support, and sync state are complicated. NudgeAI should not overclaim health data reliability before the data path is proven.

### Problem C: Location History Is Powerful But Privacy-Sensitive

Location context can generate useful nudges, but ingesting and storing location history is sensitive. Location history should remain local/private unless a stronger consent, retention, and deletion model is explicitly designed.

## 5. Goals

- Document a local-first personal context rule flow.
- Define a places/rules MVP without production OAuth complexity.
- Clarify Google Fit and Health Connect direction.
- Clarify location history limitations.
- Keep all context sources optional and user-controlled.
- Protect privacy.
- Preserve the manual nudge MVP as the core product.

## 6. Non-Goals

- Do not build public scheduling SaaS yet.
- Do not build booking/public sharing in the personal context sprint.
- Do not auto-create meetings without user confirmation.
- Do not expose private calendar event titles publicly.
- Do not auto-ingest location history without explicit user action.
- Do not rely on deprecated Google Fit APIs as the long-term plan.
- Do not make health or location data required for the app.

## 7. User Stories

- As a user, I can save important places such as Gym, Home, Uni, Work, and Library.
- As a user, I can set my current location manually or with a demo location.
- As a user, I can check context rules now and get a normal nudge when conditions match.
- As a user, I can see why Google Fit or health data is missing instead of seeing a silent blank state.
- As a user, I can import location history manually for local-only context experiments.
- As a user preparing a public demo, I can use sanitized fixtures instead of private Calendar, Drive, health, or location data.

## 8. Functional Requirements

### P0

- Document the places/rules model.
- Add a demo-safe Gym Opportunity rule.
- Add context source status cards.
- Show clear data unavailable reasons.

### P1

- Keep local place/rule editing covered by tests and demo docs.
- Keep browser geolocation explicitly opt-in and page-scoped.
- Keep local context polling disabled by default and visible to the user.

### P2

- Explore Google Calendar free/busy integration after local rules are stable.
- Add notifications after rule-created nudges are stable.
- Research Health Connect as the future health data direction.
- Improve local location import UX.

## 9. Privacy Requirements

- Never expose event titles in public availability.
- Show only busy/free blocks or user-selected available windows.
- Require user approval before calendar event creation.
- Keep location handling local-only until a production privacy design exists.
- Treat health data as sensitive personal data.
- Show clear data source status and missing-permission reasons.
- Use sanitized demo mode for public demos.

## 10. Open Questions

- Should current location remain manual/debug-only or use browser geolocation while open?
- Should rules create nudges silently or require review first?
- Should calendar availability use local demo data or future free/busy first?
- What health source should replace Google Fit for future work?
- Should location stay manual import only?
