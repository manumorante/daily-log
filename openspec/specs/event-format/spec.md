## ADDED Requirements

### Requirement: Unified event schema
Every collector SHALL return a list of event dicts. Each event MUST contain: `type` (str), `timestamp` (ISO 8601 str), `source` (str), `title` (str), `context` (str with value `"work"` or `"personal"`), `meta` (dict). Events MAY contain optional enrichment fields in `meta`: `branch` (str), `task_id` (str).

#### Scenario: Git local commit event
- **WHEN** git_local collector finds a commit at 14:32 on branch `feat/sc-1234-login` in a founderz repo
- **THEN** it returns `{"type": "commit", "timestamp": "2026-02-07T14:32:00+01:00", "source": "git_local", "context": "work", "title": "feat: add rule", "meta": {"sha": "7ad5b1a", "repo": "founderz", "author": "manumorante-fdz", "branch": "feat/sc-1234-login", "task_id": "1234"}}`

#### Scenario: GitHub PR event
- **WHEN** github collector finds a PullRequestEvent on branch `feat/sc-1234-login` for user `manumorante-fdz`
- **THEN** it returns `{"type": "pr", "timestamp": "2026-02-07T10:15:00Z", "source": "github", "context": "work", "title": "Add onboarding flow", "meta": {"action": "opened", "repo": "FounderzSchool/founderz", "number": 42, "branch": "feat/sc-1234-login", "task_id": "1234"}}`

#### Scenario: Shortcut story event
- **WHEN** shortcut collector finds a story the user touched
- **THEN** it returns `{"type": "story", "timestamp": "2026-02-07T11:20:00Z", "source": "shortcut", "context": "work", "title": "Onboard AI: Basic structure", "meta": {"id": 2983, "task_id": "2983", "story_type": "feature", "workflow_state": "In Progress"}}`

#### Scenario: Personal project commit
- **WHEN** git_local collector finds a commit in `~/projects/personal/daily-log`
- **THEN** the event includes `"context": "personal"`

#### Scenario: WakaTime personal project
- **WHEN** wakatime collector finds coding time on project `"dotfiles"`
- **THEN** the event includes `"context": "personal"`

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

### Requirement: WakaTime coding_summary event
WakaTime collector SHALL emit `coding_summary` events with `type: "coding_summary"`, `source: "wakatime"`, `title` as "{project} — {human_readable_time}", and `meta` containing `project` (str), `total_seconds` (float), `languages` (dict of language name to seconds), `human_additions` (int), `human_deletions` (int).

#### Scenario: Coding summary event structure
- **WHEN** WakaTime summaries include project "founderz" with 13260 seconds, languages {"PHP": 7800, "Blade": 4920}
- **THEN** the event is `{"type": "coding_summary", "timestamp": "2026-02-06T00:00:00+01:00", "source": "wakatime", "title": "founderz — 3 hrs 41 mins", "meta": {"project": "founderz", "total_seconds": 13260, "languages": {"PHP": 7800, "Blade": 4920}, "human_additions": 120, "human_deletions": 45}}`

### Requirement: WakaTime coding_block event
WakaTime collector SHALL emit `coding_block` events with `type: "coding_block"`, `source: "wakatime"`, `title` as "{project} ({duration}min)", and `meta` containing `project` (str), `duration_seconds` (float), `human_additions` (int), `human_deletions` (int).

#### Scenario: Coding block event structure
- **WHEN** WakaTime durations include a block at Unix time 1770505200.0 for project "daily-log" with duration 482.23 seconds
- **THEN** the event is `{"type": "coding_block", "timestamp": "2026-02-08T00:00:00+01:00", "source": "wakatime", "title": "daily-log (8min)", "meta": {"project": "daily-log", "duration_seconds": 482.23, "human_additions": 39, "human_deletions": 80}}`
