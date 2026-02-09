## 1. Core estimator module

- [x] 1.1 Create `src/estimator.py` with `estimate_tasks(events: list) -> list` function signature and empty implementation returning `[]`
- [x] 1.2 Implement event grouping by explicit `task_id` — collect events with `meta.task_id` into task buckets keyed by ID
- [x] 1.3 Implement repo-based grouping — events without `task_id` grouped by `meta.repo` (last path component) or `meta.project`, with synthetic ID `"repo:<name>"`
- [x] 1.4 Implement temporal splitting within repo groups — split events more than 60 minutes apart into separate tasks with suffixed IDs
- [x] 1.5 Implement catch-all group for events with no task_id, repo, or project (`task_id: "other"`)
- [x] 1.6 Exclude `coding_summary` events from task grouping (only `coding_block` events participate)

## 2. Time attribution

- [x] 2.1 Build time windows per task: `[earliest_event - 15min, latest_event + 15min]` with project/repo name
- [x] 2.2 Attribute `coding_block` events to tasks by matching timestamp within window AND project name match (case-insensitive, last path component)
- [x] 2.3 Handle overlapping windows — split coding_block duration proportionally between matching tasks
- [x] 2.4 Calculate `coding_time_seconds` per task as sum of attributed `coding_block` durations
- [x] 2.5 Attribute `claude_session` events to tasks by project name match, calculate `session_time_seconds` from `end_time - timestamp`
- [x] 2.6 Calculate `window_seconds` per task as span from earliest to latest event timestamp

## 3. Session detection and labels

- [x] 3.1 Detect sessions within each task: sort events by timestamp, gap > 30 minutes starts new session, output `{start, end, duration_seconds}`
- [x] 3.2 Generate task labels: story title for Shortcut tasks, `"sc-{id}"` fallback, repo name for repo-based, `"Other activity"` for catch-all
- [x] 3.3 Collect unique `sources` list per task from event source fields

## 4. Pipeline integration

- [x] 4.1 Import `estimate_tasks` in `daily_log.py` and call it between `_collect_events()` and `generate_summary()`
- [x] 4.2 Update `generate_summary()` signature to accept `tasks` parameter and include task time data in the Claude prompt
- [x] 4.3 Update `_fallback_summary()` to use task time data when available (add `time_spent` to task entries)
- [x] 4.4 Update `SUMMARY_PROMPT` to instruct Claude to reference time estimates in highlight and patterns

## 5. Validation

- [x] 5.1 Run `daily-log --dry-run` and verify events still display correctly (no regression)
- [x] 5.2 Run `daily-log --no-ai` and verify fallback summary includes time data from estimator
- [x] 5.3 Run `daily-log` for a date with WakaTime and Shortcut data, verify Claude summary references time estimates
