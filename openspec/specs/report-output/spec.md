# report-output Specification

## Purpose
TBD - created by archiving change bootstrap-specs. Update Purpose after archive.
## Requirements
### Requirement: Report file structure
Reports SHALL be written as Markdown files at `{reports_dir}/YYYY/MM/YYYY-MM-DD.md`. The directory structure SHALL be created automatically.

#### Scenario: Generate report for 2026-02-09
- **WHEN** a report is generated for date 2026-02-09
- **THEN** it is saved at `{reports_dir}/2026/02/2026-02-09.md`

### Requirement: Report content format
Each report SHALL contain: rendered markdown summary, a horizontal rule, then a `<details>` block with raw JSON event data inside a code fence.

#### Scenario: Report with summary and raw data
- **WHEN** a report is generated
- **THEN** the file contains the markdown summary followed by `---` and `<details><summary>Raw data</summary>` with the JSON events

### Requirement: Markdown rendering
`_render_markdown(date, summary)` SHALL render a summary dict into markdown with sections: header (date), highlight text, patterns/risks as bullet list, completed tasks, in-progress tasks, and code groups.

#### Scenario: Summary with all sections populated
- **WHEN** summary has highlight, patterns, tasks (done + active), and code groups
- **THEN** all sections are rendered in order with appropriate headers

#### Scenario: Empty summary
- **WHEN** summary has empty arrays and no highlight
- **THEN** only the date header is rendered

### Requirement: Skip unchanged reports
`_has_changes(log_file, raw)` SHALL compare the raw JSON in an existing report's `<details>` block with current raw data. If identical, the report SHALL NOT be regenerated.

#### Scenario: Data unchanged
- **WHEN** the raw JSON matches the existing report's embedded data
- **THEN** the report is not regenerated and a "No new changes" message is shown

#### Scenario: Data changed
- **WHEN** the raw JSON differs from the existing report
- **THEN** the report is regenerated with new data

#### Scenario: No existing report
- **WHEN** no report file exists for the date
- **THEN** a new report is always generated

