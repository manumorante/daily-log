## MODIFIED Requirements

### Requirement: Claude returns structured JSON
The summarizer prompt SHALL instruct Claude to return a JSON object, not markdown. The response MUST be parseable as JSON. The prompt SHALL include task-grouped data with time estimates when available, in addition to raw events.

#### Scenario: Successful JSON response
- **WHEN** Claude receives events, tasks with time estimates, and the prompt
- **THEN** it returns a valid JSON object with keys: `highlight`, `code`, `tasks`, `patterns`, `risks`

#### Scenario: Invalid JSON from Claude
- **WHEN** Claude returns a response that is not valid JSON
- **THEN** the system falls back to `_fallback_summary` without crashing

#### Scenario: Tasks data included in prompt
- **WHEN** the estimator produces 3 tasks with coding_time_seconds and session data
- **THEN** the summarizer prompt includes the tasks summary so Claude can reference time spent in highlight and patterns

### Requirement: JSON response schema
The JSON object SHALL contain: `highlight` (str, 2-3 sentences), `code` (list of groups), `tasks` (list), `patterns` (list of str), `risks` (list of str). Empty sections SHALL be empty arrays, not omitted. The `tasks` list MAY include `time_spent` (str, human-readable) when time data is available from the estimator.

#### Scenario: Code groups
- **WHEN** Claude identifies related commits
- **THEN** `code` contains `[{"group": "AI onboarding setup", "items": ["Config rules .agents/rules", "Centralize AI config"]}]`

#### Scenario: Tasks with time data
- **WHEN** Claude analyzes shortcut stories and receives task time estimates
- **THEN** `tasks` contains `[{"id": 2983, "name": "Onboard AI: Basic structure", "status": "in_progress", "note": "Main story of the day", "time_spent": "1h 45min coding"}]`

#### Scenario: Patterns include time observations
- **WHEN** Claude receives tasks with session data showing two work blocks
- **THEN** `patterns` contains observations like `["Worked on login in two sessions: 1h 30min morning, 45min afternoon"]`

#### Scenario: No activity in a section
- **WHEN** there are no shortcut stories
- **THEN** `tasks` is `[]` (empty array)

### Requirement: Fallback summary from events
When Claude API is unavailable, `_fallback_summary` SHALL generate the same JSON schema from raw events and task estimates: empty highlight, code groups by repo, tasks from story events enriched with time data when available, empty patterns and risks.

#### Scenario: Fallback generates valid JSON schema
- **WHEN** Claude API fails or --no-ai is used
- **THEN** the system produces a dict with the same keys (highlight, code, tasks, patterns, risks)

#### Scenario: Fallback includes time data
- **WHEN** Claude API fails but estimator produced tasks with coding_time_seconds > 0
- **THEN** the fallback tasks include `time_spent` derived from the estimator data
