## ADDED Requirements

### Requirement: Context detection by repository path
The collector SHALL import `WORK_PATH_PATTERNS` from `src/context` and add `"context": "work"` to events if any pattern in the list appears in the repo path, otherwise `"context": "personal"`.

#### Scenario: Work repository path
- **WHEN** collecting commits from `/Users/manumorante/projects/founderz/backend`
- **THEN** all events have `"context": "work"` (path contains `"founderz/"`)

#### Scenario: Personal repository path
- **WHEN** collecting commits from `/Users/manumorante/projects/personal/daily-log`
- **THEN** all events have `"context": "personal"` (no work pattern matches)

#### Scenario: Multiple repos with mixed contexts
- **WHEN** `git_repos` config includes both `/path/to/founderz/backend` and `/path/to/personal/daily-log`
- **THEN** events from founderz repos have `"context": "work"` and events from personal repos have `"context": "personal"`
