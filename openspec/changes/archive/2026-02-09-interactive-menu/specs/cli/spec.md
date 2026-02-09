## MODIFIED Requirements

### Requirement: CLI arguments
The CLI SHALL accept: `--date DATE` (default: today), `--no-ai`, `--dry-run`, `--clear`, `--setup`, `--output-dir` (hidden). When any flag is passed, the CLI SHALL execute directly without showing the menu (backward-compatible mode).

#### Scenario: No arguments
- **WHEN** `daily-log` is run with no arguments on a TTY
- **THEN** it shows the interactive menu

#### Scenario: No arguments on non-TTY
- **WHEN** `daily-log` is run with no arguments and stdout is not a TTY
- **THEN** it generates today's report directly (backward-compatible)

#### Scenario: Specific date flag
- **WHEN** `daily-log --date 2026-02-05` is run
- **THEN** it generates a report for 2026-02-05 directly without showing the menu

#### Scenario: Any flag bypasses menu
- **WHEN** any CLI flag is passed (--date, --dry-run, --no-ai, --clear, --setup)
- **THEN** the command executes directly without the interactive menu

### Requirement: Orchestration loop
The main function SHALL run all registered collectors in order, display progress with Rich spinners for each, flatten events, check for changes, generate summary, and save the report.

#### Scenario: Collector fails
- **WHEN** a collector raises an exception
- **THEN** the error is displayed and the collector is recorded with an error, but other collectors continue

#### Scenario: Missing sources warning
- **WHEN** some but not all sources are configured
- **THEN** unconfigured sources are listed as warnings before collection begins
