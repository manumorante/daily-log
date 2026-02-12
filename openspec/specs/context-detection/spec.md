# context-detection Specification

## Purpose
Logic for classifying events as work or personal context in each collector.

## Requirements

### Requirement: Context field in all events
Every collector SHALL add a `context` field to each event with value `"work"` or `"personal"`. Events without context SHALL default to `"personal"` during report generation.

#### Scenario: Work event
- **WHEN** github collector creates an event for username `manumorante-fdz`
- **THEN** the event includes `"context": "work"`

#### Scenario: Personal event
- **WHEN** git local collector creates an event for a repo in `~/projects/personal/`
- **THEN** the event includes `"context": "personal"`

### Requirement: GitHub context detection
GitHub collector SHALL classify events as work if the username matches `WORK_GITHUB_USERNAME` from `src/context`, otherwise personal.

#### Scenario: Work GitHub account
- **WHEN** github collector processes events for user `manumorante-fdz`
- **THEN** all events have `"context": "work"`

#### Scenario: Personal GitHub account
- **WHEN** github collector processes events for user `manumorante`
- **THEN** all events have `"context": "personal"`

### Requirement: Git local context detection
Git local collector SHALL classify events as work if any pattern in `WORK_PATH_PATTERNS` from `src/context` appears in the repo path, otherwise personal.

#### Scenario: Work repository path
- **WHEN** git local collector processes commits from `/Users/manumorante/projects/founderz/backend`
- **THEN** all events have `"context": "work"` (matches pattern `"founderz/"`)

#### Scenario: Personal repository path
- **WHEN** git local collector processes commits from `/Users/manumorante/projects/personal/daily-log`
- **THEN** all events have `"context": "personal"` (no work pattern matches)

### Requirement: WakaTime context detection
WakaTime collector SHALL classify events as work if any keyword in `WORK_PROJECT_KEYWORDS` from `src/context` appears in the project name (case-insensitive), otherwise personal.

#### Scenario: Work project
- **WHEN** wakatime collector processes a coding summary for project `"founderz-backend"`
- **THEN** the event has `"context": "work"` (matches keyword `"founderz"`)

#### Scenario: Personal project
- **WHEN** wakatime collector processes a coding block for project `"daily-log"`
- **THEN** the event has `"context": "personal"` (no work keyword matches)

### Requirement: Shortcut context detection
Shortcut collector SHALL always classify events as work.

#### Scenario: All shortcut events are work
- **WHEN** shortcut collector creates any story or epic event
- **THEN** the event has `"context": "work"`

### Requirement: Context filtering in main flow
`daily_log.py` SHALL filter all collected events by context field before generating reports.

#### Scenario: Filter work events
- **WHEN** generating work report
- **THEN** only events with `"context": "work"` are included

#### Scenario: Filter personal events
- **WHEN** generating personal report
- **THEN** only events with `"context": "personal"` are included

#### Scenario: Missing context field
- **WHEN** an event is missing the `context` field
- **THEN** it defaults to `"personal"` and a warning is logged
