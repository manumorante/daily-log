## MODIFIED Requirements

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

#### Scenario: Claude Code session event
- **WHEN** claude_code collector finds a session in project `founderz` with 12 messages from 02:19 to 03:40
- **THEN** it returns `{"type": "claude_session", "timestamp": "2026-02-07T02:19:00+01:00", "source": "claude_code", "title": "reescribir CLAUDE.md del proyecto", "meta": {"project": "founderz", "session_id": "6d2eae38", "message_count": 12, "end_time": "2026-02-07T03:40:00+01:00"}}`
