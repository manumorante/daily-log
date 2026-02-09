# cli Specification

## Purpose
TBD - created by archiving change bootstrap-specs. Update Purpose after archive.
## Requirements
### Requirement: CLI arguments
The CLI SHALL accept: `--date DATE` (default: today), `--no-ai`, `--dry-run`, `--clear`, `--setup`, `--output-dir` (hidden).

#### Scenario: No arguments
- **WHEN** `daily-log` is run with no arguments
- **THEN** it generates today's report with AI summary

#### Scenario: Specific date
- **WHEN** `daily-log --date 2026-02-05` is run
- **THEN** it generates a report for 2026-02-05

### Requirement: Dry run mode
`--dry-run` SHALL collect events from all sources and print the JSON to stdout without generating a report file.

#### Scenario: Dry run
- **WHEN** `daily-log --dry-run` is run
- **THEN** collected events are printed as JSON and no file is written

### Requirement: No-AI mode
`--no-ai` SHALL use the fallback summary generator instead of calling the Claude API.

#### Scenario: No-AI report
- **WHEN** `daily-log --no-ai` is run
- **THEN** a report is generated using `_fallback_summary` without calling the Claude API

### Requirement: Clear report
`--clear` SHALL delete the report file for the given date if it exists.

#### Scenario: Clear existing report
- **WHEN** `daily-log --clear` is run and a report exists for today
- **THEN** the report file is deleted

#### Scenario: Clear non-existent report
- **WHEN** `daily-log --clear` is run and no report exists
- **THEN** a "No report for {date}" message is shown

### Requirement: Setup delegation
`--setup` SHALL delegate to `src/setup.py` by replacing the current process.

#### Scenario: Run setup
- **WHEN** `daily-log --setup` is run
- **THEN** `setup.py` is executed via `os.execvp`

### Requirement: Orchestration loop
The main function SHALL run all registered collectors in order, display progress for each, flatten events, check for changes, generate summary, and save the report.

#### Scenario: Collector fails
- **WHEN** a collector raises an exception
- **THEN** the error is displayed and the collector is recorded with an error, but other collectors continue

#### Scenario: Missing sources warning
- **WHEN** some but not all sources are configured
- **THEN** unconfigured sources are listed as warnings before collection begins

