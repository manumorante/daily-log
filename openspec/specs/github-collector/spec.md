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
- `PushEvent` → one `commit` event per commit (title = first line of message, meta: sha, repo)
- `PullRequestEvent` → one `pr` event (title = PR title, meta: action, repo, number)
- `IssuesEvent` → one `issue` event (title = issue title, meta: action, repo)
- `PullRequestReviewEvent` → one `review` event (title = PR title, meta: repo)

Unknown event types SHALL be silently skipped.

#### Scenario: PushEvent with 3 commits
- **WHEN** a PushEvent contains 3 commits
- **THEN** 3 separate `commit` events are emitted, each with `sha` truncated to 7 chars

#### Scenario: Unknown event type
- **WHEN** a `WatchEvent` is encountered
- **THEN** it is skipped without error

