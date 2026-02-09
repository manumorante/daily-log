## Context

Collectors emit events with timestamps but no way to link them to tasks. The `sc-XXXX` pattern in git branch names is the strongest signal for connecting commits to Shortcut stories. PRs also carry branch info via the GitHub API. This change enriches events with `branch` and `task_id` fields, and documents the grouping model for future time estimation.

Current git_local format: `--format=%h|%s|%an|%aI` (no branch). GitHub PR events don't include `head.ref`. GitHub PushEvent commits don't include `payload.ref`. Shortcut events already have story IDs in `meta.id`.

## Goals / Non-Goals

**Goals:**
- Add `branch` to git_local commit events, github PR events, and github PushEvent commits
- Add optional `task_id` to the event schema, populated when a deterministic signal exists
- Define the task-linking model (how events map to tasks)
- Document time estimation heuristics for future implementation

**Non-Goals:**
- Implementing time estimation or session detection (future change)
- Building a task grouping engine (this change only enriches data and documents the model)
- Cross-collector dedup (e.g., same commit in git_local and github PushEvent) — deferred to the grouping layer, both emit enriched data independently

## Decisions

### Extract branch per commit via `git log --format`
Use `git log --format=%h|%s|%an|%aI|%D` and parse `%D` (ref names) to get the branch. `%D` gives comma-separated refs like `HEAD -> main, origin/main`. For commits not at branch tips, use `git branch --contains <sha>` as fallback.

**Alternative**: Use `git name-rev --name-only <sha>`. Rejected — it gives tags and relative refs (e.g., `main~3`), not the actual branch name. `git branch --contains` gives all branches containing the commit, which is what we need.

**Simpler alternative**: For each commit, run `git log --all --format=%h|%D` once per repo to build a sha→branch map, then look up each commit. This avoids N subprocess calls per repo. Use the first non-HEAD, non-remote branch as the branch name.

### Extract `task_id` from branch name pattern
Parse `sc-XXXX` from branch names using regex `sc-(\d+)`. This maps directly to Shortcut story IDs. If no `sc-XXXX` pattern, `task_id` is omitted (not null — simply absent from meta).

**Alternative**: Use PR body/title for story linking. Rejected — branch is more reliable and consistent.

### Branch from GitHub Events API payloads
Both event types carry branch info, no extra API call needed:
- **`PullRequestEvent`**: `payload.pull_request.head.ref` — the source branch name.
- **`PushEvent`**: `payload.ref` — the full ref (e.g., `refs/heads/feat/sc-1234`). Strip `refs/heads/` prefix to get the branch name.

This means a commit pushed to GitHub gets `branch` and `task_id` even if the repo isn't in `git_repos`. The same commit may appear in both `git_local` and `github` — cross-collector dedup by SHA is deferred to the future grouping layer.

### `task_id` and `branch` as optional fields in `meta`
Add these as optional keys inside `meta`, not as top-level event fields. This keeps the core schema (`type`, `timestamp`, `source`, `title`, `meta`) unchanged. Collectors add them when the data is available.

**Alternative**: Add them as top-level optional fields. Rejected — breaks the principle that the 5 core fields are always present. `meta` is the right place for source-specific enrichment.

### Shortcut events already have `task_id`
`shortcut.py` already puts `id` in `meta`. Rename it to also include `task_id` as an alias for consistency. The `id` field stays for backward compatibility.

### Task-linking model (documented, not implemented)
The linking priority:
1. **Explicit `task_id`** — from `sc-XXXX` in branch name or Shortcut story ID
2. **Repo-based grouping** — events without `task_id` grouped by repo name
3. **Temporal proximity** — events within 30min of each other likely belong to same work session

This model is documented in the spec but not coded in this change.

## Risks / Trade-offs

- **[Branch detection accuracy]** → A commit may appear in multiple branches. We pick the first non-main, non-master branch. If ambiguous, the branch field may be imprecise. Acceptable — `task_id` extraction from the pattern is still reliable.
- **[Performance: git branch --contains]** → Running per-commit could be slow for repos with many branches. Mitigated by building the sha→branch map once per repo.
- **[Not all branches have sc-XXXX]** → Personal projects, open source, or poorly named branches won't produce a `task_id`. This is fine — `task_id` is optional.
