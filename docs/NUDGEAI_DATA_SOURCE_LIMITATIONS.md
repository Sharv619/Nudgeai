# NudgeAI Data Source Limitations

## Why Google Fit Data May Not Appear

Possible reasons:

- Google Fit API access is limited/deprecated.
- The account may not have usable Fit data.
- Required OAuth scopes may not be configured.
- Token may not include Fit permissions.
- Device/app may not be syncing data into Google Fit.
- Local sync script may be reading demo/fallback files.
- Dashboard may not have a connected frontend path for real Fit data.

## Direction

Do not build around Google Fit as the long-term core. Research Health Connect or use demo fixtures for portfolio demos.

## Why Location History May Require Manual Download

Possible reasons:

- Location history is sensitive.
- Google Maps Timeline data is not the same as simple Calendar/Drive metadata.
- Automatic access may not be available in the same way as Calendar/Drive.
- Manual export/import keeps the local prototype honest and private.
- Raw location data must never be committed.

## Direction

Use local-only import and sanitized demo data. Do not build cloud location ingestion until privacy design is complete.

## Why Calendar/Drive Works But Fit/Location Does Not

Calendar and Drive have clearer API/data paths in the current repo. Fit and Location are more sensitive, more fragmented, or require different platform approaches.

## What Dashboard Should Show Instead

Add source status cards:

| Source | Status | User Message |
|---|---|---|
| Calendar | Connected / Demo / Missing Token | Calendar data available / not connected |
| Drive | Connected / Demo / Missing Token | Drive metadata available / not connected |
| Health | Not configured / deprecated path | Health data requires future Health Connect research |
| Location | Manual import required | Upload local export or use demo fixture |

## Public Demo Rule

Public demos must use sanitized fixtures only.
