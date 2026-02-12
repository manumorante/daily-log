## ADDED Requirements

### Requirement: Context constants module
The system SHALL provide a `src/context.py` module that exports constants for identifying work-related patterns across all collectors.

#### Scenario: Module import
- **WHEN** a collector imports `from src.context import WORK_GITHUB_USERNAME`
- **THEN** the constant is available and contains the work GitHub username

### Requirement: Work GitHub username constant
`WORK_GITHUB_USERNAME` SHALL be set to `"manumorante-fdz"` (the Founderz GitHub account).

#### Scenario: GitHub collector uses constant
- **WHEN** github collector checks if `username == WORK_GITHUB_USERNAME`
- **THEN** events from `manumorante-fdz` are classified as work

### Requirement: Work path patterns constant
`WORK_PATH_PATTERNS` SHALL be a list containing path substrings that indicate work context: `["founderz/"]`.

#### Scenario: Git local collector matches path
- **WHEN** git local collector checks if any pattern in `WORK_PATH_PATTERNS` appears in repo path `/Users/manumorante/projects/founderz/backend`
- **THEN** it matches `"founderz/"` and classifies events as work

### Requirement: Work project keywords constant
`WORK_PROJECT_KEYWORDS` SHALL be a list containing project name substrings that indicate work context: `["founderz"]`.

#### Scenario: WakaTime collector matches project
- **WHEN** wakatime collector checks if any keyword in `WORK_PROJECT_KEYWORDS` appears in project name `"founderz-backend"`
- **THEN** it matches `"founderz"` and classifies events as work

### Requirement: Work-only sources constant
`WORK_ONLY_SOURCES` SHALL be a list of source names that are always work context: `["shortcut"]`.

#### Scenario: Shortcut collector uses constant
- **WHEN** a collector checks if its source name is in `WORK_ONLY_SOURCES`
- **THEN** shortcut events are automatically classified as work
