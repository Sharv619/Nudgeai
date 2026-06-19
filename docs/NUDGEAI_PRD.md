# NudgeAI PRD

## 1. Product Name

NudgeAI

## 2. One-Line Description

NudgeAI helps users turn scattered obligations and context into clear, timely nudges they can review, snooze, and complete.

## 3. Problem Statement

People accumulate commitments across notes, calendar events, documents, messages, places, and personal routines. Important follow-ups often get lost because reminders are either manual, too generic, or disconnected from context. NudgeAI should reduce that friction by converting messy input into actionable nudges and resurfacing them at useful times.

## 4. Target Users

Primary users:
- Students and early-career professionals managing meetings, applications, events, errands, and personal goals.
- Solo builders/freelancers tracking follow-ups, tasks, and relationship maintenance.

Secondary users:
- Busy professionals who want lightweight personal CRM-style reminders.
- Productivity enthusiasts who want context-aware reminders without building complex automations.

## 5. User Personas

### Persona 1: Aarav

- Name: Aarav
- Role: University student and hackathon participant
- Pain: Misses follow-ups after events and forgets prep tasks before meetings.
- Current workaround: Calendar reminders, scattered notes, and memory.
- Desired outcome: A simple list of next actions with due times and context.
- Why NudgeAI helps: It can turn messy event notes into reviewable nudges and show them in one place.

### Persona 2: Maya

- Name: Maya
- Role: Job seeker
- Pain: Tracks applications, recruiter conversations, and follow-up deadlines manually.
- Current workaround: Spreadsheet plus calendar reminders.
- Desired outcome: Follow-up reminders that include who, why, and when.
- Why NudgeAI helps: It can extract follow-up tasks from notes and keep status visible.

### Persona 3: Chris

- Name: Chris
- Role: Freelancer
- Pain: Forgets invoice follow-ups, meeting prep, and client check-ins.
- Current workaround: Email stars, task apps, and calendar blocks.
- Desired outcome: A reliable nudge queue with snooze, complete, and priority.
- Why NudgeAI helps: It can centralize obligations and eventually connect to calendar/email context.

## 6. Product Goals

- Provide a reliable core nudge lifecycle: create, view, update, snooze, dismiss, complete.
- Let users review AI-suggested nudges before saving anything.
- Make due and overdue nudges obvious.
- Keep personal data handling transparent and minimal.
- Support a credible 3-minute portfolio demo without fake production claims.

## 7. Non-Goals

- Do not build email/calendar/CRM integrations before the manual nudge loop works.
- Do not auto-send messages or take actions without explicit user review.
- Do not claim production readiness before auth, access control, privacy, tests, and deployment are fixed.
- Do not make the MVP an MCP/RAG platform UI.
- Do not optimize for team collaboration yet.

## 8. Core Use Cases

1. Create a nudge manually with title, context, due date, status, and priority.
2. View pending, due today, overdue, completed, snoozed, and dismissed nudges.
3. Complete, snooze, or dismiss a nudge.
4. Paste messy notes and receive structured AI-suggested nudges.
5. Review and edit AI suggestions before saving.
6. See why an AI suggestion was created from the original input.
7. Run a demo with seeded sample nudges and known limitations.

## 9. Functional Requirements

| Priority | Requirement | Description | Acceptance Criteria |
|---|---|---|---|
| P0 | Manual nudge creation | User can create a nudge without AI. | Form saves title, context, due date, priority, status. Saved nudge appears in list. |
| P0 | Nudge list | User can see all nudges grouped/filterable by status. | Pending, due today, overdue, completed, snoozed, dismissed are visible. |
| P0 | Status lifecycle | User can complete, snooze, dismiss, and reopen nudges. | Status changes persist after reload. |
| P0 | Persistence | Nudge data survives server restart. | Data stored in DB or documented local store, not only React state. |
| P1 | AI extraction | User can paste messy text and get structured suggestions. | API returns validated JSON with title, context, due date, priority, confidence, source span/reason. |
| P1 | Human review | AI suggestions are not saved automatically. | User can edit, discard, or save each suggestion. |
| P1 | Reminder timing | Due/overdue state is computed from due date/reminder time. | Overdue nudges appear without manual refresh hacks. |
| P1 | Error states | API/AI failures are visible and recoverable. | UI shows retryable errors without fake success data. |
| P2 | Settings | User can set timezone and reminder preferences. | Settings persist and affect due-time display. |
| P3 | Integrations | Calendar/email/contact integrations create candidate nudges. | Imported suggestions are reviewable and source-labeled. |

## 10. Non-Functional Requirements

- Security: User data endpoints require auth before deployment; no open CORS in production.
- Privacy: Notes, nudges, calendar/location data, and AI prompts are sensitive and must have retention/deletion rules.
- Reliability: Core nudge CRUD must work without AI provider availability.
- Latency: Manual CRUD should respond under 500 ms locally; AI extraction should show progress and timeout gracefully.
- Accessibility: Keyboard navigation, visible focus states, semantic forms, sufficient contrast.
- Maintainability: One canonical backend and documented setup path.
- Observability: Structured logs for API errors without logging full sensitive note contents.

## 11. User Stories

| Story | Acceptance Criteria |
|---|---|
| As a user, I want to create a nudge manually, so that I can capture obligations quickly. | Required fields validated; saved nudge appears in pending list; page reload preserves it. |
| As a user, I want to paste messy notes, so that NudgeAI can suggest tasks I might miss. | Suggestions return as structured JSON; user sees confidence and source reason. |
| As a user, I want to review AI suggestions, so that bad suggestions are not saved. | Each suggestion can be edited, discarded, or saved independently. |
| As a user, I want to snooze a nudge, so that I can defer it without losing it. | Snoozed nudge leaves pending list and returns when snooze time arrives. |
| As a user, I want to complete a nudge, so that I know what is done. | Completion timestamp is stored and completed nudges can be viewed. |
| As a user, I want to see overdue nudges, so that I can recover missed commitments. | Overdue state is computed from due/reminder time and visible in dashboard. |

## 12. MVP Scope

The smallest useful version is a local/demo-ready web app where a single user can manually create nudges, view them in a dashboard, update status, and optionally paste messy notes for AI-suggested nudges that must be reviewed before saving.

## 13. Out of Scope

- Multi-user teams
- External email sending
- Full Google Calendar/Gmail production integration
- Mobile app
- Proactive background agent
- Relationship gap detection
- Advanced analytics
- Auto-actions without user confirmation

## 14. Success Metrics

- Activation metric: User creates or saves 3 nudges in first session.
- Engagement metric: User returns to the dashboard and updates at least 1 nudge status.
- Completion metric: At least 50% of created demo nudges can be completed or snoozed during demo flow.
- Quality metric: At least 70% of AI-suggested nudges from demo notes are accepted after minor or no edits.
- Reliability metric: Manual nudge CRUD passes automated tests and works without AI keys.

## 15. Risks

- Product risk: Current repo direction is split between RAG dashboard and nudge lifecycle.
- Technical risk: Multiple backend entry points make setup/deployment fragile.
- AI risk: Prompt outputs may hallucinate due dates or obligations without validation.
- Privacy risk: Calendar, location, notes, and prompts are sensitive.
- Execution risk: Building integrations before the core loop will increase complexity without demo value.

## 16. Dependencies

- React/Vite frontend
- FastAPI backend
- Local or hosted database
- Optional AI provider for extraction
- Optional embedding/RAG stack after MVP
- Google APIs only after core loop is stable

## 17. Open Questions

- Is MVP single-user local-first or authenticated web app?
- Which backend file becomes canonical?
- Should existing RAG/MCP features remain in MVP UI or move behind an experimental section?
- Which AI provider should be used for structured extraction?
- What data can be safely committed as demo fixtures?
- What reminder channel should V1 support first: in-app, browser notification, email, or calendar event?
