## ADDED Requirements

### Requirement: Unified event schema
Every collector SHALL return a list of event dicts. Each event MUST contain: `type` (str), `timestamp` (ISO 8601 str), `source` (str), `title` (str), `meta` (dict).

#### Scenario: Git local commit event
- **WHEN** git_local collector finds a commit at 14:32
- **THEN** it returns `{"type": "commit", "timestamp": "2026-02-07T14:32:00+01:00", "source": "git_local", "title": "feat: add rule", "meta": {"sha": "7ad5b1a9d", "repo": "founderz", "author": "manumorante-fdz"}}`

#### Scenario: GitHub PR event
- **WHEN** github collector finds a PullRequestEvent
- **THEN** it returns `{"type": "pr", "timestamp": "2026-02-07T10:15:00Z", "source": "github", "title": "Add onboarding flow", "meta": {"action": "opened", "repo": "FounderzSchool/founderz", "number": 42}}`

#### Scenario: Shortcut story event
- **WHEN** shortcut collector finds a story the user touched
- **THEN** it returns `{"type": "story", "timestamp": "2026-02-07T11:20:00Z", "source": "shortcut", "title": "Onboard AI: Basic structure", "meta": {"id": 2983, "story_type": "feature", "workflow_state": "In Progress"}}`

#### Scenario: Shortcut epic event
- **WHEN** shortcut collector finds an epic updated today
- **THEN** it returns `{"type": "epic", "timestamp": "2026-02-07T11:25:00Z", "source": "shortcut", "title": "Onboard AI to Project", "meta": {"id": 2982, "state": "in progress"}}`

### Requirement: Collector return format
Each collector SHALL return a dict with `source` (str) and `events` (list of event dicts). If skipped, it SHALL return `{"source": "...", "status": "skipped", "reason": "..."}`.

#### Scenario: Collector with events
- **WHEN** github collector finds 3 events for the date
- **THEN** it returns `{"source": "github", "events": [...]}`

#### Scenario: Collector skipped
- **WHEN** shortcut token is not configured
- **THEN** it returns `{"source": "shortcut", "status": "skipped", "reason": "no token"}`

### Requirement: Timestamps from each source
git_local SHALL use `git log --format=%aI` for author date. github SHALL use `created_at` from the events API. shortcut SHALL use `changed_at` from the story history endpoint.

#### Scenario: Git log includes timestamp
- **WHEN** git_local runs git log
- **THEN** format string includes `%aI` and the timestamp is included in each event

#### Scenario: Shortcut uses history timestamp
- **WHEN** shortcut collector checks story history for member filtering
- **THEN** it captures the `changed_at` value and uses it as the event timestamp
