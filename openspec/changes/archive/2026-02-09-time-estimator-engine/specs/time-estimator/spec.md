## ADDED Requirements

### Requirement: Public interface
The module SHALL expose a single function `estimate_tasks(events: list) -> list` that takes a flat list of event dicts and returns a list of task dicts with time estimates.

#### Scenario: Basic invocation
- **WHEN** `estimate_tasks` is called with a list of events from multiple collectors
- **THEN** it returns a list of task dicts, each with keys: `task_id`, `label`, `events`, `coding_time_seconds`, `session_time_seconds`, `window_seconds`, `sessions`, `sources`

#### Scenario: Empty events
- **WHEN** `estimate_tasks` is called with an empty list
- **THEN** it returns an empty list

### Requirement: Task grouping by explicit task_id
Events with `meta.task_id` SHALL be grouped into tasks keyed by that ID. The `task_id` field in the output matches `meta.task_id` from the events.

#### Scenario: Events with same task_id
- **WHEN** three events have `meta.task_id` = "1234" (two commits and one PR)
- **THEN** a single task is created with `task_id: "1234"` containing all three events

#### Scenario: Events with different task_ids
- **WHEN** events have `meta.task_id` values "1234" and "5678"
- **THEN** two separate tasks are created, one for each ID

### Requirement: Task grouping by repo
Events without `meta.task_id` SHALL be grouped by repository. The repo name is derived from `meta.repo` (last path component, e.g., `"FounderzSchool/founderz"` becomes `"founderz"`) or `meta.project`. The synthetic `task_id` SHALL be `"repo:<name>"`.

#### Scenario: Commits without task_id in same repo
- **WHEN** three commits have no `meta.task_id` but share `meta.repo` = "manumorante/daily-log"
- **THEN** a task is created with `task_id: "repo:daily-log"` containing all three

#### Scenario: WakaTime summary without task_id
- **WHEN** a `coding_summary` event has `meta.project` = "daily-log" and no `meta.task_id`
- **THEN** it groups with the `"repo:daily-log"` task

### Requirement: Temporal splitting within repo groups
Within a repo-based group, events more than 60 minutes apart (by timestamp) SHALL be split into separate tasks. The split tasks receive suffixed IDs like `"repo:daily-log:1"`, `"repo:daily-log:2"`.

#### Scenario: Commits spread across the day
- **WHEN** repo "daily-log" has commits at 10:00, 10:30, 15:00, 15:20
- **THEN** two tasks are created: `"repo:daily-log:1"` (10:00, 10:30) and `"repo:daily-log:2"` (15:00, 15:20)

#### Scenario: Commits within 60 minutes
- **WHEN** repo "daily-log" has commits at 10:00, 10:20, 10:55
- **THEN** one task is created with all three commits

### Requirement: Catch-all group for ungrouped events
Events with no `meta.task_id`, no `meta.repo`, and no `meta.project` SHALL be placed in a task with `task_id: "other"`.

#### Scenario: Event with no grouping signals
- **WHEN** an event has no task_id, repo, or project in meta
- **THEN** it is placed in the `"other"` task

### Requirement: WakaTime coding_block attribution
`coding_block` events SHALL be attributed to tasks by matching their timestamp against task time windows AND their `meta.project` against the task's repo/project name. A task's time window is `[earliest_event - 15min, latest_event + 15min]`.

#### Scenario: Block within task window and matching project
- **WHEN** task "1234" has commits in repo "founderz" between 10:00 and 12:00, and a coding_block at 11:15 for project "founderz"
- **THEN** the coding_block is attributed to task "1234"

#### Scenario: Block outside all task windows
- **WHEN** a coding_block at 09:00 for project "founderz" exists but no task has events near that time for that project
- **THEN** the coding_block is not attributed to any task

#### Scenario: Block matching multiple tasks (overlapping windows)
- **WHEN** task "1234" (founderz, 10:00-11:30) and task "5678" (founderz, 11:00-12:30) both cover a coding_block at 11:15
- **THEN** the block's duration is split proportionally between the two tasks

### Requirement: Coding time calculation
Each task's `coding_time_seconds` SHALL be the sum of `meta.duration_seconds` from all WakaTime coding_blocks attributed to that task.

#### Scenario: Two blocks attributed to task
- **WHEN** task "1234" has two attributed coding_blocks with durations 300s and 450s
- **THEN** `coding_time_seconds` is 750

#### Scenario: No blocks attributed
- **WHEN** no coding_blocks match task "1234"
- **THEN** `coding_time_seconds` is 0

### Requirement: Claude Code session attribution
`claude_session` events SHALL be attributed to tasks by matching `meta.project` (last path component) to the task's repo/project name. Session duration is `meta.end_time - timestamp`.

#### Scenario: Session matching task project
- **WHEN** task "repo:daily-log" exists and a claude_session has `meta.project` = "personal/ia/daily-log"
- **THEN** the session's duration is added to the task's `session_time_seconds`

#### Scenario: Session with no matching task
- **WHEN** a claude_session has project "notes-app" but no task exists for that repo
- **THEN** a new `"repo:notes-app"` task is created containing the session

### Requirement: Window time calculation
Each task's `window_seconds` SHALL be the duration from the earliest event timestamp to the latest event timestamp within that task. If a task has only one event, `window_seconds` is 0.

#### Scenario: Task spanning two hours
- **WHEN** task "1234" has events at 10:00 and 12:00
- **THEN** `window_seconds` is 7200

#### Scenario: Single event task
- **WHEN** task "repo:notes" has one event at 14:00
- **THEN** `window_seconds` is 0

### Requirement: Session detection
Within each task, consecutive events sorted by timestamp SHALL be grouped into sessions. A gap of more than 30 minutes between consecutive events starts a new session. Each session has `start`, `end`, and `duration_seconds`.

#### Scenario: Continuous activity
- **WHEN** task "1234" has events at 10:00, 10:15, 10:40, 10:55
- **THEN** one session: `{start: 10:00, end: 10:55, duration_seconds: 3300}`

#### Scenario: Gap creates new session
- **WHEN** task "1234" has events at 10:00, 10:20, 14:00, 14:30
- **THEN** two sessions: `{start: 10:00, end: 10:20, ...}` and `{start: 14:00, end: 14:30, ...}`

### Requirement: Task label generation
Each task SHALL have a human-readable `label`. For tasks with a Shortcut `task_id`, the label is derived from the first `story` event title if available, otherwise `"sc-{task_id}"`. For repo-based tasks, the label is the repo name. For `"other"`, the label is `"Other activity"`.

#### Scenario: Task with story event
- **WHEN** task "1234" contains a story event with title "Onboard AI: Basic structure"
- **THEN** `label` is "Onboard AI: Basic structure"

#### Scenario: Task with only commits
- **WHEN** task "1234" has commits but no story event
- **THEN** `label` is "sc-1234"

#### Scenario: Repo-based task
- **WHEN** task "repo:daily-log" exists
- **THEN** `label` is "daily-log"

### Requirement: Sources list
Each task SHALL include a `sources` list containing the unique `source` values from its events (e.g., `["git_local", "github", "wakatime"]`).

#### Scenario: Task with events from multiple sources
- **WHEN** task "1234" has events from git_local, github, and wakatime
- **THEN** `sources` is `["git_local", "github", "wakatime"]`

### Requirement: Exclude summary events from grouping
`coding_summary` events (WakaTime daily totals) SHALL NOT be included in task grouping or time attribution. Only `coding_block` events are used for time attribution. `coding_summary` events are informational and remain in the raw events list.

#### Scenario: coding_summary ignored for grouping
- **WHEN** events include both `coding_summary` and `coding_block` for project "founderz"
- **THEN** only `coding_block` events are attributed to tasks; `coding_summary` events are excluded from task grouping
