## ADDED Requirements

### Requirement: Claude returns structured JSON
The summarizer prompt SHALL instruct Claude to return a JSON object, not markdown. The response MUST be parseable as JSON.

#### Scenario: Successful JSON response
- **WHEN** Claude receives events and the prompt
- **THEN** it returns a valid JSON object with keys: `highlight`, `code`, `tasks`, `patterns`, `risks`

#### Scenario: Invalid JSON from Claude
- **WHEN** Claude returns a response that is not valid JSON
- **THEN** the system falls back to `_fallback_summary` without crashing

### Requirement: JSON response schema
The JSON object SHALL contain: `highlight` (str, 2-3 sentences), `code` (list of groups), `tasks` (list), `patterns` (list of str), `risks` (list of str). Empty sections SHALL be empty arrays, not omitted.

#### Scenario: Code groups
- **WHEN** Claude identifies related commits
- **THEN** `code` contains `[{"group": "AI onboarding setup", "items": ["Config rules .agents/rules", "Centralize AI config"]}]`

#### Scenario: Tasks with notes
- **WHEN** Claude analyzes shortcut stories
- **THEN** `tasks` contains `[{"id": 2983, "name": "Onboard AI: Basic structure", "status": "in_progress", "note": "Main story of the day"}]`

#### Scenario: Patterns detected
- **WHEN** Claude finds temporal patterns in events
- **THEN** `patterns` contains observations like `["15 commits in founderz between 10:00-12:00 = intense work session"]`

#### Scenario: No activity in a section
- **WHEN** there are no shortcut stories
- **THEN** `tasks` is `[]` (empty array)

### Requirement: Terminal shows only highlight
After generating the summary, the terminal SHALL display only the `highlight` field, not the full report.

#### Scenario: Display after generation
- **WHEN** the report is generated successfully
- **THEN** terminal shows the highlight text and the file path

### Requirement: Markdown rendered from JSON
The .md file SHALL be rendered from the JSON fields, not from raw Claude text. Each non-empty section becomes a markdown heading with formatted content.

#### Scenario: Full report render
- **WHEN** JSON has highlight, 2 code groups, 1 task, and 1 pattern
- **THEN** the .md file contains sections for summary, code, tasks, and patterns

#### Scenario: Empty sections omitted
- **WHEN** JSON has empty `risks` array
- **THEN** the .md file does not include a risks section

### Requirement: Fallback summary from events
When Claude API is unavailable, `_fallback_summary` SHALL generate the same JSON schema from raw events: empty highlight, code groups by repo, tasks from story events, empty patterns and risks.

#### Scenario: Fallback generates valid JSON schema
- **WHEN** Claude API fails or --no-ai is used
- **THEN** the system produces a dict with the same keys (highlight, code, tasks, patterns, risks)
