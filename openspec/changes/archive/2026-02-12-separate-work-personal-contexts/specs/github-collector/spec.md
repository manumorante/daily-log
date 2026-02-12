## ADDED Requirements

### Requirement: Context detection by username
The collector SHALL import `WORK_GITHUB_USERNAME` from `src/context` and add `"context": "work"` to events if the username matches, otherwise `"context": "personal"`.

#### Scenario: Work account events
- **WHEN** collecting events for user `manumorante-fdz` (matches `WORK_GITHUB_USERNAME`)
- **THEN** all events have `"context": "work"`

#### Scenario: Personal account events
- **WHEN** collecting events for user `manumorante` (does not match `WORK_GITHUB_USERNAME`)
- **THEN** all events have `"context": "personal"`

#### Scenario: Mixed accounts in API response
- **WHEN** the API returns events from multiple GitHub accounts
- **THEN** each event's context is determined by its own username field
