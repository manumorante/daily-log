## ADDED Requirements

### Requirement: Main menu display
When `daily-log` is run with no arguments on a TTY, it SHALL display an interactive menu using `beaupy.select()` with the following options in order: "Report de hoy", "Report de ayer", "Report de otra fecha", "Borrar report", "Setup", "Salir".

#### Scenario: No arguments on TTY
- **WHEN** `daily-log` is run with no arguments and stdout is a TTY
- **THEN** an interactive menu is displayed with arrow-key navigation

#### Scenario: No arguments on non-TTY
- **WHEN** `daily-log` is run with no arguments and stdout is not a TTY
- **THEN** today's report is generated directly (current default behavior)

### Requirement: Menu loop
After an action completes, the menu SHALL be displayed again. The loop continues until the user selects "Salir" or presses Ctrl+C.

#### Scenario: Action completes
- **WHEN** user selects "Report de hoy" and the report finishes generating
- **THEN** the menu is displayed again

#### Scenario: Exit via menu
- **WHEN** user selects "Salir"
- **THEN** the program exits cleanly

#### Scenario: Exit via Ctrl+C
- **WHEN** user presses Ctrl+C at any point
- **THEN** the program exits cleanly without a traceback

### Requirement: Report de hoy
Selecting "Report de hoy" SHALL generate today's report using the standard collection and summarization flow.

#### Scenario: Generate today
- **WHEN** user selects "Report de hoy"
- **THEN** collectors run for today's date and a report is generated

### Requirement: Report de ayer
Selecting "Report de ayer" SHALL generate yesterday's report.

#### Scenario: Generate yesterday
- **WHEN** user selects "Report de ayer"
- **THEN** collectors run for yesterday's date and a report is generated

### Requirement: Report de otra fecha
Selecting "Report de otra fecha" SHALL prompt for a date using `beaupy.prompt()` with today's date as default, then generate the report for that date.

#### Scenario: Custom date entry
- **WHEN** user selects "Report de otra fecha"
- **THEN** a text prompt appears asking for a date in YYYY-MM-DD format with today's date pre-filled

#### Scenario: Valid date entered
- **WHEN** user enters "2026-01-15"
- **THEN** collectors run for 2026-01-15 and a report is generated

### Requirement: Borrar report
Selecting "Borrar report" SHALL prompt for a date using `beaupy.prompt()` with today's date as default, then delete the report file for that date if it exists.

#### Scenario: Delete existing report
- **WHEN** user selects "Borrar report" and enters a date with an existing report
- **THEN** the report file is deleted and a confirmation message is shown

#### Scenario: Delete non-existent report
- **WHEN** user selects "Borrar report" and enters a date with no report
- **THEN** a "No report for {date}" message is shown

### Requirement: Setup delegation
Selecting "Setup" SHALL delegate to `setup.py` the same way `--setup` does.

#### Scenario: Setup from menu
- **WHEN** user selects "Setup"
- **THEN** the setup wizard runs and upon completion the menu is displayed again

### Requirement: App header
The menu SHALL be preceded by an app header showing the app name styled with Rich.

#### Scenario: Header display
- **WHEN** the menu is displayed
- **THEN** an app header with "daily-log" is shown above the menu options
