## MODIFIED Requirements

### Requirement: Report file structure
Reports SHALL be written as Markdown files at `{reports_dir}/{context}/YYYY/MM/YYYY-MM-DD.md` where `context` is either `"work"` or `"personal"`. The directory structure SHALL be created automatically.

#### Scenario: Generate work report for 2026-02-09
- **WHEN** a work report is generated for date 2026-02-09
- **THEN** it is saved at `{reports_dir}/work/2026/02/2026-02-09.md`

#### Scenario: Generate personal report for 2026-02-09
- **WHEN** a personal report is generated for date 2026-02-09
- **THEN** it is saved at `{reports_dir}/personal/2026/02/2026-02-09.md`

#### Scenario: Generate both reports
- **WHEN** both work and personal reports are generated for the same date
- **THEN** two separate files are created in their respective context subdirectories

## ADDED Requirements

### Requirement: Context filtering
`write_report()` SHALL accept a `context` parameter (`"work"` or `"personal"`) and generate a report containing only events matching that context.

#### Scenario: Work report contains only work events
- **WHEN** `write_report()` is called with `context="work"` and a mix of work/personal events
- **THEN** the generated report includes only events with `"context": "work"`

#### Scenario: Personal report contains only personal events
- **WHEN** `write_report()` is called with `context="personal"` and a mix of work/personal events
- **THEN** the generated report includes only events with `"context": "personal"`

### Requirement: Generate work context by default
When no context filter is specified via interactive menu, the system SHALL generate a work report for the selected date.

#### Scenario: Default generation
- **WHEN** no context is explicitly selected in the interactive menu
- **THEN** only `work/YYYY/MM/DD.md` is generated

#### Scenario: Menu selection "both"
- **WHEN** user selects context "both" in the interactive menu
- **THEN** both `work/YYYY/MM/DD.md` and `personal/YYYY/MM/DD.md` are generated

#### Scenario: No events for a context
- **WHEN** a date has no events for a given context
- **THEN** the report file is still generated with a "No activity recorded" message (keeps a trace that generation ran)
