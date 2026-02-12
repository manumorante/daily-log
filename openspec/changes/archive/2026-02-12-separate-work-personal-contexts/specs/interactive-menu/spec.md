## MODIFIED Requirements

### Requirement: Today's report
Selecting "Today's report" SHALL prompt for context selection (work / personal / both), then generate report(s) for today using the standard collection and summarization flow.

#### Scenario: Generate today work only
- **WHEN** user selects "Today's report" and then selects context "work"
- **THEN** collectors run for today's date and only the work report is generated

#### Scenario: Generate today both contexts
- **WHEN** user selects "Today's report" and then selects context "both"
- **THEN** collectors run for today's date and both work and personal reports are generated

### Requirement: Yesterday's report
Selecting "Yesterday's report" SHALL prompt for context selection (work / personal / both), then generate report(s) for yesterday.

#### Scenario: Generate yesterday personal only
- **WHEN** user selects "Yesterday's report" and then selects context "personal"
- **THEN** collectors run for yesterday's date and only the personal report is generated

### Requirement: Custom date report
Selecting "Report for a date" SHALL prompt for a date using `beaupy.prompt()` with today's date as default, then prompt for context selection (work / personal / both), then generate report(s) for that date.

#### Scenario: Custom date with context selection
- **WHEN** user selects "Report for a date", enters "2026-01-15", and selects context "work"
- **THEN** collectors run for 2026-01-15 and only the work report is generated

### Requirement: Delete report
Selecting "Delete report" SHALL prompt for a date using `beaupy.prompt()` with today's date as default, then prompt for context selection (work / personal / both), then delete the selected report file(s) for that date if they exist.

#### Scenario: Delete work report only
- **WHEN** user selects "Delete report", enters a date, and selects context "work"
- **THEN** only the work report file for that date is deleted if it exists

#### Scenario: Delete both reports
- **WHEN** user selects "Delete report", enters a date, and selects context "both"
- **THEN** both work and personal report files for that date are deleted if they exist

#### Scenario: Delete non-existent context report
- **WHEN** user selects "Delete report", enters a date, selects "personal", but only work report exists
- **THEN** a "No personal report for {date}" message is shown

## ADDED Requirements

### Requirement: Context selection prompt
After selecting a report action (today / yesterday / custom date / delete), the menu SHALL prompt for context using `beaupy.select()` with options: "work" (default), "personal", "both".

#### Scenario: Context prompt display
- **WHEN** user selects any report action
- **THEN** a context selection menu is displayed with three options

#### Scenario: Default to work
- **WHEN** user presses Enter without changing selection
- **THEN** context defaults to "work" and only the work report is generated
