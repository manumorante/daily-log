## Why

Two minor DRY violations detected during codebase review: a duplicated time-formatting function and an inlined pattern that already has a shared helper.

## What Changes

- **Deduplicate time formatting**: `daily_log._format_time()` and `wakatime._format_duration()` are identical. Consolidate into one shared function.
- **Share `_branch_meta` helper**: `github.py` has `_branch_meta(branch)` that wraps `extract_task_id`. `git_local.py` inlines the same logic. Move `_branch_meta` to `_utils.py` so both collectors use it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This is a pure internal refactor with no behavior change.

## Impact

- `src/collectors/_utils.py` — gains `branch_meta()` and `format_duration()`
- `src/collectors/github.py` — imports `branch_meta` from `_utils` instead of local `_branch_meta`
- `src/collectors/git_local.py` — imports `branch_meta` from `_utils`, removes inline logic
- `src/collectors/wakatime.py` — imports `format_duration` from `_utils`, removes local `_format_duration`
- `src/daily_log.py` — imports `format_duration` from `collectors._utils`, removes local `_format_time`
