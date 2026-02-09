## 1. Consolidate shared utilities in `_utils.py`

- [x] 1.1 Add `format_duration(seconds)` to `src/collectors/_utils.py` (move from `wakatime.py`)
- [x] 1.2 Add `branch_meta(branch)` to `src/collectors/_utils.py` (move from `github.py`)

## 2. Update consumers

- [x] 2.1 `wakatime.py`: import `format_duration` from `_utils`, remove local `_format_duration`
- [x] 2.2 `github.py`: import `branch_meta` from `_utils`, remove local `_branch_meta`
- [x] 2.3 `git_local.py`: import `branch_meta` from `_utils`, replace inline logic (lines 127-131)
- [x] 2.4 `daily_log.py`: import `format_duration` from `collectors._utils`, remove local `_format_time`

## 3. Verify

- [x] 3.1 Run `daily-log --dry-run` to confirm no regressions
