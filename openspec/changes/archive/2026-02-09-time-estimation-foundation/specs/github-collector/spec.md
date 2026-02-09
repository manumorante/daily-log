## MODIFIED Requirements

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
