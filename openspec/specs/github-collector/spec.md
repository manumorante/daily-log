# github-collector Specification

## Purpose
TBD - created by archiving change bootstrap-specs. Update Purpose after archive.
## Requirements
### Requirement: Collector signature and registration
`collect_github(config, date)` SHALL follow the standard collector signature. It SHALL be registered in `src/collectors/__init__.py` in the `ALL` list as `("GitHub", collect_github)`.

#### Scenario: No credentials configured
- **WHEN** `github_token` or `github_username` is missing from config
- **THEN** it returns `{"source": "github", "status": "skipped", "reason": "no token/username"}`

#### Scenario: API error
- **WHEN** the GitHub API returns an error
- **THEN** it returns `{"source": "github", "events": [], "error": "<message>"}`

### Requirement: Fetch and filter GitHub events
The collector SHALL call `GET /users/{username}/events?per_page=100` and filter events to the requested date by comparing `created_at[:10]` with the date parameter.

#### Scenario: Day with mixed events
- **WHEN** the API returns events from multiple days
- **THEN** only events matching the requested date are processed

### Requirement: Parse event types
The collector SHALL parse these GitHub event types into structured events:
- `PushEvent` → one `commit` event per commit (title = first line of message, meta: sha, repo, branch, and optionally task_id). Branch SHALL be extracted from `payload.ref` by stripping the `refs/heads/` prefix.
- `PullRequestEvent` → one `pr` event (title = PR title, meta: action, repo, number, branch, and optionally task_id). Branch SHALL be extracted from `payload.pull_request.head.ref`.
- `IssuesEvent` → one `issue` event (title = issue title, meta: action, repo)
- `PullRequestReviewEvent` → one `review` event (title = PR title, meta: repo)

Unknown event types SHALL be silently skipped. For events with a branch, `task_id` SHALL be derived by matching `sc-(\d+)` on the branch name.

#### Scenario: PushEvent with 3 commits
- **WHEN** a PushEvent contains 3 commits and `payload.ref` is `refs/heads/feat/sc-1234-login`
- **THEN** 3 separate `commit` events are emitted, each with `sha` truncated to 7 chars, `meta.branch: "feat/sc-1234-login"`, and `meta.task_id: "1234"`

#### Scenario: PushEvent on main branch
- **WHEN** a PushEvent has `payload.ref` = `refs/heads/main`
- **THEN** commit events have `meta.branch: "main"` and `meta.task_id` is absent

#### Scenario: PullRequestEvent with sc-XXXX branch
- **WHEN** a PullRequestEvent has `payload.pull_request.head.ref` = `fix/sc-567-bug`
- **THEN** the pr event has `meta.branch: "fix/sc-567-bug"` and `meta.task_id: "567"`

#### Scenario: Unknown event type
- **WHEN** a `WatchEvent` is encountered
- **THEN** it is skipped without error


### Requirement: Context detection by username
The collector SHALL import `WORK_GITHUB_USERNAME` from `src/context` and add `"context": "work"` to events if the username matches, otherwise `"context": "personal"`.

#### Scenario: Work account events
- **WHEN** collecting events for user `manumorante-fdz` (matches `WORK_GITHUB_USERNAME`)
- **THEN** all events have `"context": "work"`

#### Scenario: Personal account events
- **WHEN** collecting events for user `manumorante` (does not match `WORK_GITHUB_USERNAME`)
- **THEN** all events have `"context": "personal"`

#### Scenario: Mixed accounts in API response
- **WHEN** the API returns events from multiple GitHub accounts
- **THEN** each event's context is determined by its own username field
