## Why

Collectors now emit events enriched with `branch`, `task_id`, and temporal data (WakaTime coding blocks, Claude Code session durations), but nothing consumes these signals. The pipeline passes raw events directly to the summarizer. There is no module that groups events by task, detects work sessions, or estimates time spent — the core value proposition that makes daily-log more than a list of events. This is the missing "Step 2" between collection and summarization.

## What Changes

- Create a new `src/estimator.py` module that takes the flat `events[]` list and produces `tasks[]` — a grouped, time-estimated structure
- Group events by task using the priority model defined in `task-linking` spec: explicit `task_id` first, then repo-based, then temporal proximity
- Cross-reference WakaTime `coding_block` events with commit/PR time windows to attribute real coding time to specific tasks
- Detect work sessions (continuous activity periods) per task
- Produce a `tasks[]` output structure with estimated time, contributing events, and session boundaries per task
- Integrate the estimator into the main pipeline between `_collect_events()` and `generate_summary()`, passing enriched task data to the summarizer

## Capabilities

### New Capabilities
- `time-estimator`: Engine that groups events by task, cross-references coding blocks with commit windows, and estimates time per task. Input: flat events list. Output: structured tasks with time estimates.

### Modified Capabilities
- `json-summarizer`: The summarizer prompt receives task-grouped data with time estimates in addition to raw events, enabling richer time-aware summaries.

## Impact

- `src/estimator.py`: New file — the estimation engine
- `src/daily_log.py`: Insert estimator call between `_collect_events()` and `generate_summary()`. Update summarizer prompt to leverage time data.
- No new dependencies — pure Python stdlib (datetime, collections)
- No config changes — the estimator works with whatever events are available
