# NudgeAI Booking and Availability Plan

## 1. Feature Summary

NudgeAI may support a lightweight availability/booking flow where the user can expose selected available windows and approve meeting requests.

## 2. Why This Belongs In NudgeAI

Booking creates commitments, and commitments become nudges.

Example flow:

Visitor requests meeting -> user approves -> calendar event created or manual nudge created -> NudgeAI reminds user to prepare and follow up.

## 3. MVP Booking Flow

Do not start with a full Calendly clone.

MVP:

1. User defines available windows manually.
2. Visitor submits a meeting request.
3. Request appears as a nudge.
4. User approves or rejects manually.
5. Approved request can later create a calendar event.

## 4. Future Calendar-Backed Flow

1. User connects Google Calendar.
2. NudgeAI reads free/busy blocks.
3. NudgeAI suggests availability windows.
4. Visitor requests time.
5. User approves.
6. NudgeAI creates calendar event.
7. NudgeAI creates prep/follow-up nudges.

Google Calendar Freebusy can return busy time ranges for calendars, and Calendar Events insert can create events. Both require careful authorization, OAuth scopes, and user consent.

## 5. Data Model Draft

```ts
type AvailabilityWindow = {
  id: string;
  userId: string;
  weekday?: number;
  startsAt: string;
  endsAt: string;
  timezone: string;
  source: "manual" | "calendar_suggested";
  isBookable: boolean;
};

type BookingStatus = "requested" | "approved" | "rejected" | "cancelled" | "event_created";

type BookingRequest = {
  id: string;
  requesterName: string;
  requesterEmail?: string;
  title: string;
  notes?: string;
  requestedStart: string;
  requestedEnd: string;
  timezone: string;
  status: BookingStatus;
  createdAt: string;
  approvedAt?: string;
};

type MeetingPreference = {
  defaultDurationMinutes: number;
  bufferMinutes: number;
  timezone: string;
  minNoticeHours: number;
  allowedWeekdays: number[];
};

type BookingNudgeLink = {
  bookingRequestId: string;
  nudgeId: string;
  linkType: "approval_task" | "prep" | "follow_up";
};
```

## 6. API Planning

Possible MVP endpoints:

- `GET /api/availability`
- `POST /api/availability`
- `POST /api/booking-requests`
- `GET /api/booking-requests`
- `PATCH /api/booking-requests/{id}`

Later endpoints:

- `POST /api/calendar/freebusy`
- `POST /api/calendar/create-event`

## 7. UI Planning

- Availability settings
- Public/request form or demo request form
- Booking request inbox
- Booking request detail
- Approval confirmation
- Prep/follow-up nudge creation

## 8. Privacy Rules

- Public booking pages must not expose private calendar titles.
- Only show available slots or broad availability windows.
- User controls which windows are bookable.
- Do not create calendar events automatically without approval.
- Document every calendar scope before requesting authorization.

## 9. MVP Vs Later

| Capability | MVP | Later |
|---|---|---|
| Manual availability windows | yes | yes |
| Public booking request form | maybe local/demo | yes |
| Google Calendar free/busy | no | yes |
| Calendar event creation | no | yes |
| Auto-created prep nudges | no | yes |
| Approval before booking | yes | yes |

## 10. Risks

- Scope creep into a Calendly clone.
- Calendar privacy leakage.
- OAuth complexity.
- Timezone bugs.
- Spam booking requests.
- Event creation without consent.

## 11. Recommended Build Order

1. Manual availability model.
2. Booking request becomes nudge.
3. Booking request dashboard.
4. Approval/rejection.
5. Calendar free/busy read.
6. Event creation after approval.
