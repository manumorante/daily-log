## MODIFIED Requirements

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
