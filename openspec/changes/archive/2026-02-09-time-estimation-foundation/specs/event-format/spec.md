## ADDED Requirements

### Requirement: Optional branch field in meta
Collectors that have access to branch information SHALL include `meta.branch` (str) in events. The value is the short branch name (e.g., `feat/sc-1234-login`, not `refs/heads/feat/sc-1234-login`). If no branch is available, the field SHALL be omitted.

#### Scenario: Git local commit with branch
- **WHEN** git_local collector finds a commit on branch `feat/sc-1234-login`
- **THEN** the event includes `meta.branch: "feat/sc-1234-login"`

#### Scenario: GitHub PushEvent commit with branch
- **WHEN** github collector processes a PushEvent with `payload.ref` = `refs/heads/feat/sc-1234-login`
- **THEN** the event includes `meta.branch: "feat/sc-1234-login"`

#### Scenario: GitHub PR event with branch
- **WHEN** github collector processes a PullRequestEvent with `payload.pull_request.head.ref` = `feat/sc-1234-login`
- **THEN** the event includes `meta.branch: "feat/sc-1234-login"`

#### Scenario: Event without branch info
- **WHEN** a shortcut story event is emitted
- **THEN** `meta.branch` is absent (shortcut has no branch concept)

### Requirement: Optional task_id field in meta
Collectors SHALL include `meta.task_id` (str) when a deterministic signal links the event to a task. The value is the Shortcut story ID as a string. If no signal exists, the field SHALL be omitted.

#### Scenario: Event with task_id from branch
- **WHEN** a commit has `meta.branch` = `feat/sc-1234-login`
- **THEN** the event includes `meta.task_id: "1234"`

#### Scenario: Shortcut event with task_id
- **WHEN** a story event has `meta.id` = 2983
- **THEN** the event also includes `meta.task_id: "2983"`

## MODIFIED Requirements

### Requirement: Unified event schema
Every collector SHALL return a list of event dicts. Each event MUST contain: `type` (str), `timestamp` (ISO 8601 str), `source` (str), `title` (str), `meta` (dict). Events MAY contain optional enrichment fields in `meta`: `branch` (str), `task_id` (str).

#### Scenario: Git local commit event
- **WHEN** git_local collector finds a commit at 14:32 on branch `feat/sc-1234-login`
- **THEN** it returns `{"type": "commit", "timestamp": "2026-02-07T14:32:00+01:00", "source": "git_local", "title": "feat: add rule", "meta": {"sha": "7ad5b1a", "repo": "founderz", "author": "manumorante-fdz", "branch": "feat/sc-1234-login", "task_id": "1234"}}`

#### Scenario: GitHub PR event
- **WHEN** github collector finds a PullRequestEvent on branch `feat/sc-1234-login`
- **THEN** it returns `{"type": "pr", "timestamp": "2026-02-07T10:15:00Z", "source": "github", "title": "Add onboarding flow", "meta": {"action": "opened", "repo": "FounderzSchool/founderz", "number": 42, "branch": "feat/sc-1234-login", "task_id": "1234"}}`

#### Scenario: Shortcut story event
- **WHEN** shortcut collector finds a story the user touched
- **THEN** it returns `{"type": "story", "timestamp": "2026-02-07T11:20:00Z", "source": "shortcut", "title": "Onboard AI: Basic structure", "meta": {"id": 2983, "task_id": "2983", "story_type": "feature", "workflow_state": "In Progress"}}`

#### Scenario: Shortcut epic event
- **WHEN** shortcut collector finds an epic updated today
- **THEN** it returns `{"type": "epic", "timestamp": "2026-02-07T11:25:00Z", "source": "shortcut", "title": "Onboard AI to Project", "meta": {"id": 2982, "state": "in progress"}}`

#### Scenario: Claude Code session event
- **WHEN** claude_code collector finds a session in project `founderz` with 12 messages from 02:19 to 03:40
- **THEN** it returns `{"type": "claude_session", "timestamp": "2026-02-07T02:19:00+01:00", "source": "claude_code", "title": "reescribir CLAUDE.md del proyecto", "meta": {"project": "founderz", "session_id": "6d2eae38", "message_count": 12, "end_time": "2026-02-07T03:40:00+01:00"}}`

#### Scenario: GitHub PushEvent commit
- **WHEN** github collector finds a PushEvent on branch `fix/sc-567-bug`
- **THEN** the commit events include `meta.branch: "fix/sc-567-bug"` and `meta.task_id: "567"`

#### Scenario: Event without enrichment fields
- **WHEN** a commit is on branch `main` (no sc-XXXX pattern)
- **THEN** `meta.branch` is `"main"` and `meta.task_id` is absent
