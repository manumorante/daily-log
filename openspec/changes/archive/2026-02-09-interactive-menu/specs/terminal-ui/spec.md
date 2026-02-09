## MODIFIED Requirements

### Requirement: Rich-based color system
The UI SHALL use a shared `rich.console.Console` instance with Rich's built-in color names (green, yellow, red, blue, cyan, dim). No custom Theme, no ANSI 256 codes, no emojis.

#### Scenario: Colored output
- **WHEN** `green("text")` is called on a TTY
- **THEN** it returns text styled with Rich's built-in green

#### Scenario: No-color mode
- **WHEN** stdout is not a TTY or `NO_COLOR` env is set
- **THEN** all color functions return plain text without formatting

### Requirement: Output helpers
The UI SHALL provide functions: `header(title)`, `ok(text)`, `skip(text)`, `warn(text)`, `err(text)`, `item(text)`, `info(text)`, `run(text)`, `done(text)`, `separator()`. All output SHALL be indented with 2 spaces. Internal implementation SHALL use `rich.console.Console.print()`.

#### Scenario: Header display
- **WHEN** `header("daily-log 2026-02-09")` is called
- **THEN** it prints the title in blue followed by a dim separator line using Rich

#### Scenario: Done display
- **WHEN** `done("path/to/file")` is called
- **THEN** it prints a green bullet followed by the text, with a leading blank line

## ADDED Requirements

### Requirement: Spinner support
The UI SHALL provide a `spinner(message)` context manager that displays a Rich status spinner while a block of code executes.

#### Scenario: Spinner during collection
- **WHEN** `with ui.spinner("Collecting GitHub..."):` is used
- **THEN** a spinner animation is shown while the block runs, then disappears

#### Scenario: Spinner on non-TTY
- **WHEN** `spinner()` is used and stdout is not a TTY
- **THEN** the message is printed once without animation
