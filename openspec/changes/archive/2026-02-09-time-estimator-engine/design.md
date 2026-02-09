## Context

The `time-estimation-foundation` change enriched collectors with `branch` and `task_id` fields and documented the task-linking model. The pipeline currently passes flat `events[]` directly from `_collect_events()` to `generate_summary()` — no grouping, no time estimation. WakaTime emits `coding_summary` (total seconds per project) and `coding_block` (timestamped activity blocks with duration). Claude Code emits sessions with `start_time` and `end_time`. Git commits and PRs carry `task_id` derived from branch names. All the raw signals exist; nothing connects them.

The tool may evolve from "run once at end of day" to "check anytime during the day" — the estimator must work with partial-day data, not assume the day is complete.

## Goals / Non-Goals

**Goals:**
- Create `src/estimator.py` as a single independent module
- Group events into tasks using the priority model: explicit `task_id` > repo > temporal proximity
- Cross-reference WakaTime `coding_block` timestamps with commit/PR time windows to attribute real coding time to tasks
- Detect work sessions (continuous activity within a task)
- Produce a `tasks[]` structure that the summarizer can consume alongside raw events
- Work correctly whether run mid-day (partial data) or end-of-day (complete data)

**Non-Goals:**
- Persisting state between runs (each invocation is stateless, processes current events)
- Cross-collector dedup (same commit in git_local and github — both contribute to time windows)
- Billing-grade accuracy (this is for developer insight, not invoicing)
- New CLI flags or interactive modes (deferred to a future change)

## Decisions

### Single public function: `estimate_tasks(events) -> list[dict]`

The module exposes one function. It takes the flat events list and returns a list of task dicts. This keeps the integration point minimal — one line in `daily_log.py`.

**Alternative**: A class-based estimator with configurable strategies. Rejected — over-engineering for the current scope. A function with internal helpers is sufficient.

### Task grouping: three-tier priority

1. **Explicit `task_id`**: Events with `meta.task_id` are grouped by that ID. This is the strongest signal (from `sc-XXXX` in branch names or Shortcut story IDs).
2. **Repo-based**: Events without `task_id` are grouped by `meta.repo` or `meta.project`. Creates synthetic task IDs like `repo:daily-log`.
3. **Temporal proximity**: Within a repo group, events more than 60 minutes apart are split into separate tasks. This prevents "all day on repo X" from being a single block.

Events that match no group (no task_id, no repo, no project) are collected under a catch-all `"other"` task.

**Alternative**: Only group by `task_id`, treat everything else as ungrouped. Rejected — most personal projects don't use Shortcut, so repo-based grouping is essential for useful output.

### Time attribution: WakaTime coding_blocks as primary signal

WakaTime `coding_block` events have real timestamps and real durations — they are measured, not inferred. The strategy:

1. **Build time windows per task**: For each task, define the window as `[earliest_event_timestamp - 15min, latest_event_timestamp + 15min]`. The 15-minute margin accounts for coding that happens before/after a commit.
2. **Assign coding_blocks to tasks**: Each `coding_block` is assigned to the task whose window contains its timestamp AND whose project name matches the block's `meta.project`. If a block matches multiple tasks (overlapping windows, same project), split proportionally by window overlap.
3. **Sum assigned blocks**: The task's `coding_time` is the sum of `duration_seconds` from its assigned coding_blocks.
4. **Session time from Claude Code**: `claude_session` events with matching project are assigned similarly. Their duration (`end_time - timestamp`) is added as `session_time`.
5. **Fallback: window heuristic**: If no WakaTime blocks match a task, estimate from the event window: `(last_timestamp - first_timestamp)` capped at a reasonable maximum (e.g., the window itself, no inflation).

**Alternative**: Distribute WakaTime total proportionally by commit count. Rejected — loses temporal precision. Blocks have timestamps; using them is both more accurate and not significantly more complex.

**Alternative**: Use WakaTime `coding_summary` (total per project) as a budget and distribute. Rejected — `coding_block` gives per-block granularity which is what we need for task-level attribution.

### Project name matching between WakaTime and git

WakaTime project names (e.g., `"founderz"`, `"daily-log"`) must match git repo names or meta.project values from other collectors. The matching is:
- Exact match on the last path component of `meta.repo` (e.g., `"FounderzSchool/founderz"` → `"founderz"`)
- Case-insensitive comparison
- Claude Code `meta.project` is already simplified (e.g., `"personal/ia/daily-log"` → last component `"daily-log"`)

No configuration needed for most cases. If a WakaTime project name doesn't match any task's repo, its blocks remain unassigned (reported separately as unattributed coding time).

### Output structure: tasks list

```python
{
    "task_id": "1234",           # or "repo:daily-log" or "other"
    "label": "sc-1234 login",    # human-readable: from story title or repo name
    "events": [...],             # original events belonging to this task
    "coding_time_seconds": 3720, # from WakaTime blocks (measured)
    "session_time_seconds": 1800,# from Claude Code sessions
    "window_seconds": 5400,      # first event to last event span
    "sessions": [                # detected activity sessions
        {"start": "...", "end": "...", "duration_seconds": 2400}
    ],
    "sources": ["git_local", "github", "wakatime", "shortcut"]
}
```

The summarizer receives both `events[]` (raw, as before) and `tasks[]` (grouped with times). This is additive — no breaking change to the existing flow.

### Session detection within tasks

A "session" is a period of continuous activity on a task. Within a task's events (sorted by timestamp), a gap of more than 30 minutes between consecutive events starts a new session. WakaTime coding_blocks assigned to the task also contribute to session boundaries.

Sessions help answer "how many times did I context-switch to this task today?"

### Integration: minimal insertion

```python
# In daily_log.py main(), after _collect_events():
events = _collect_events(collected)
tasks = estimate_tasks(events)  # NEW

# Pass both to summarizer:
summary = generate_summary(config, date, events, tasks)
```

The summarizer prompt is updated to include task summaries with time data, giving Claude richer context for the highlight and patterns sections.

## Risks / Trade-offs

- **[WakaTime project name mismatch]** → Some projects may use different names in WakaTime vs git. Mitigation: case-insensitive last-component matching handles most cases. Unmatched blocks are reported separately, not lost.
- **[Overlapping task windows]** → Two tasks on the same project may have overlapping time windows. Mitigation: coding_blocks in overlap zones are split proportionally. Acceptable for insight-level accuracy.
- **[No WakaTime configured]** → If WakaTime is not set up, `coding_time_seconds` will be 0 for all tasks. Mitigation: the window heuristic provides a fallback estimate, and Claude Code sessions give partial time data. The estimator degrades gracefully.
- **[Partial day data]** → Running mid-day means windows are open-ended. Mitigation: the estimator is stateless and processes whatever events exist. No assumption about day completeness.
- **[Performance]** → Iterating over all events multiple times (grouping, then block assignment, then session detection). Mitigation: daily event counts are in the low hundreds at most. No optimization needed.
