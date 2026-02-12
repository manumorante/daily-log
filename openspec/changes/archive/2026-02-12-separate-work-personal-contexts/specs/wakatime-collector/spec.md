## ADDED Requirements

### Requirement: Context detection by project name
The collector SHALL import `WORK_PROJECT_KEYWORDS` from `src/context` and add `"context": "work"` to events if any keyword in the list appears in the project name (case-insensitive), otherwise `"context": "personal"`.

#### Scenario: Work project detected
- **WHEN** collecting coding summary for project `"founderz-backend"`
- **THEN** the event has `"context": "work"` (project name contains keyword `"founderz"`)

#### Scenario: Personal project detected
- **WHEN** collecting coding block for project `"daily-log"`
- **THEN** the event has `"context": "personal"` (no work keyword matches)

#### Scenario: Case-insensitive matching
- **WHEN** collecting events for project `"Founderz-Backend"` (mixed case)
- **THEN** the event has `"context": "work"` (case-insensitive match on `"founderz"`)

#### Scenario: Mixed projects in same day
- **WHEN** WakaTime summaries include both `"founderz"` and `"daily-log"` projects
- **THEN** founderz events have `"context": "work"` and daily-log events have `"context": "personal"`
