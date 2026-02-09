## Why

Collectors emit events with timestamps but lack the data needed to group events by task and estimate work time. Commits don't carry branch names (which contain Shortcut IDs like `sc-XXXX`), PRs don't include their source branch, and there's no way to detect work sessions or interleaved tasks. Before building time calculation, we need richer data from collectors and a clear model for linking events to tasks.

## What Changes

- Enrich `git_local` collector to include the branch name of each commit (the key signal for linking commits to Shortcut stories via `sc-XXXX` in branch names)
- Enrich `github` collector to include branch name in both PR events (`head.ref`) and PushEvent commits (`payload.ref`), and derive `task_id` from the branch pattern
- Add a `task_id` field to the event format so collectors can explicitly link events to tasks when the signal is deterministic
- Define a task-grouping model: how events get assigned to tasks (by `sc-XXXX` in branch, by repo for non-Shortcut work, by temporal proximity as fallback)
- Document time estimation heuristics for future implementation: session detection, per-event-type margins, gap handling for interleaved tasks

## Capabilities

### New Capabilities
- `task-linking`: Model for associating events with tasks. Defines `task_id` field, linking signals (branch-based, repo-based, temporal), and grouping rules. This is the foundation for time estimation.

### Modified Capabilities
- `event-format`: Add optional `task_id` and `branch` fields to the event schema. Collectors populate these when deterministic signals exist.

## Impact

- `src/collectors/git_local.py`: Extract branch name per commit, derive `task_id` from `sc-XXXX` pattern
- `src/collectors/github.py`: Extract branch from PR (`head.ref`) and PushEvent (`payload.ref`), derive `task_id`
- `src/collectors/shortcut.py`: Set `task_id` from story ID (already available)
- `openspec/specs/event-format/spec.md`: Add `task_id` and `branch` to schema
- Future: time estimation logic will consume task-grouped events (not part of this change)
