## 1. Shared task_id helper

- [x] 1.1 Create `_extract_task_id(branch)` function that matches `sc-(\d+)` and returns the ID string or None
- [x] 1.2 Place it in a shared location accessible by git_local and github collectors (e.g., `src/collectors/_utils.py`)

## 2. git_local collector: branch enrichment

- [x] 2.1 Add `_build_branch_map(repo_path)` that runs `git log --all --format=%h|%D`, parses refs, and returns a sha→branch dict (first non-HEAD, non-remote ref per sha)
- [x] 2.2 Add fallback: for shas not in the map, run `git branch --contains <sha>` and pick first non-main, non-master branch
- [x] 2.3 Enrich each commit event with `meta.branch` from the map and `meta.task_id` via `_extract_task_id`
- [x] 2.4 Verify with `--dry-run` on a repo with feature branches

## 3. github collector: branch enrichment

- [x] 3.1 In `_parse_push`, extract branch from `payload.ref` (strip `refs/heads/` prefix), add `meta.branch` and `meta.task_id`
- [x] 3.2 In `_parse_pr`, extract branch from `payload.pull_request.head.ref`, add `meta.branch` and `meta.task_id`
- [x] 3.3 Verify with `--dry-run` against real GitHub events

## 4. shortcut collector: task_id alias

- [x] 4.1 Add `meta.task_id` as string of `story_id` in story events (keep existing `meta.id` unchanged)
- [x] 4.2 Verify with `--dry-run`

## 5. Validation

- [x] 5.1 Run `daily-log --dry-run` and confirm branch/task_id appear in git_local, github, and shortcut events
- [x] 5.2 Run `daily-log` for a date with sc-XXXX branches and verify task_id extraction
