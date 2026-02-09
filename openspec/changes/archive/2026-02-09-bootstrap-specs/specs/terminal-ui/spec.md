## ADDED Requirements

### Requirement: ANSI 256 pastel color palette
The UI SHALL use ANSI 256 color codes for a pastel palette: green (114), yellow (222), red (174), blue (111), cyan (116), dim (245). No emojis.

#### Scenario: Colored output
- **WHEN** `green("text")` is called on a TTY
- **THEN** it returns `\033[38;5;114mtext\033[0m`

#### Scenario: No-color mode
- **WHEN** stdout is not a TTY
- **THEN** all color functions return plain text without ANSI codes

### Requirement: Unicode symbols
The UI SHALL define symbols: OK = green `●`, SKIP = dim `○`, WARN = yellow `▲`, ERR = red `✕`, ITEM = dim `▸`, RUN = blue `●`.

#### Scenario: Symbol display
- **WHEN** `ui.OK` is used in output
- **THEN** it displays a green `●` character (or plain `●` without color if not TTY)

### Requirement: Output helpers
The UI SHALL provide functions: `header(title)`, `ok(text)`, `skip(text)`, `warn(text)`, `err(text)`, `item(text)`, `info(text)`, `run(text)`, `done(text)`, `separator()`. All output SHALL be indented with 2 spaces.

#### Scenario: Header display
- **WHEN** `header("daily-log 2026-02-09")` is called
- **THEN** it prints the title in blue followed by a dim separator line

#### Scenario: Done display
- **WHEN** `done("path/to/file")` is called
- **THEN** it prints a green `●` followed by the text, with a leading blank line
