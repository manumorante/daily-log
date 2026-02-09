### Requirement: Token prompts use secure input
Token and API key fields SHALL use `beaupy.prompt` with `secure=True` to mask input.

#### Scenario: GitHub token input
- **WHEN** user is prompted for GitHub token
- **THEN** input is masked (characters not visible)

#### Scenario: Non-secret fields show input
- **WHEN** user is prompted for GitHub username
- **THEN** input is visible as typed

### Requirement: Yes/no questions use confirm
Boolean questions SHALL use `beaupy.confirm` instead of text input with "s/n".

#### Scenario: Auto-scan repos confirmation
- **WHEN** user is asked whether to auto-scan for repos
- **THEN** a confirm prompt appears with arrow-key y/n selection

#### Scenario: Reconfigure confirmation
- **WHEN** all sections are configured and user is asked to reconfigure
- **THEN** a confirm prompt appears with arrow-key y/n selection

### Requirement: Repo selection uses select_multiple
Git repo selection from scanned results SHALL use `beaupy.select_multiple` with checkboxes.

#### Scenario: Multiple repos found
- **WHEN** auto-scan finds 5 repos
- **THEN** user sees a checkbox list and toggles repos with space, confirms with enter

#### Scenario: All repos pre-ticked
- **WHEN** the checkbox list appears
- **THEN** all repos are ticked by default (user unticks what they don't want)

### Requirement: Section reconfigure uses select_multiple
When reconfiguring, section selection SHALL use `beaupy.select_multiple` instead of comma-separated numbers.

#### Scenario: User wants to reconfigure
- **WHEN** user confirms they want to reconfigure
- **THEN** a checkbox list of sections appears (GitHub, Shortcut, Claude API, WakaTime, Git repos)

### Requirement: Text prompts show initial value
Text prompts with existing config values SHALL use `beaupy.prompt` with `initial_value` to pre-fill the current value.

#### Scenario: Username already configured
- **WHEN** GitHub username is already "manumorante"
- **THEN** the prompt shows "manumorante" as editable initial value

#### Scenario: Empty field
- **WHEN** a field has no existing value
- **THEN** the prompt starts empty

### Requirement: All UI strings in English
All user-facing strings in setup.py SHALL be in English.

#### Scenario: Scan prompt
- **WHEN** user is asked about repo scanning
- **THEN** the prompt text is in English (e.g., "Scan for git repos automatically?")

### Requirement: Scan directories prompt
When user confirms auto-scan, the directories to scan SHALL be entered via `beaupy.prompt` with a sensible default.

#### Scenario: Default scan directories
- **WHEN** user is prompted for directories to scan
- **THEN** the default value is `~/projects`
