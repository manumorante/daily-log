# git-local-collector Specification

## Purpose
TBD - created by archiving change bootstrap-specs. Update Purpose after archive.
## Requirements
### Requirement: Collector signature and registration
`collect_git_local(config, date)` SHALL follow the standard collector signature. It SHALL be registered in `src/collectors/__init__.py` in the `ALL` list as `("Git Local", collect_git_local)`.

#### Scenario: No repos configured
- **WHEN** `git_repos` is empty or missing from config
- **THEN** it returns `{"source": "git_local", "status": "skipped", "reason": "no repos configured"}`

### Requirement: Collect commits from local repos
For each repo path in `git_repos`, the collector SHALL run `git log` with `--since={date}T00:00:00 --until={date}T23:59:59 --format=%h|%s|%an|%aI --all`. It SHALL filter by the repo's configured `user.name` as `--author`.

#### Scenario: Repo with 3 commits today
- **WHEN** a repo has 3 commits by the configured author on the requested date
- **THEN** 3 `commit` events are emitted with meta: sha, repo (basename of path), author

#### Scenario: Repo path does not exist
- **WHEN** a configured repo path does not exist on disk
- **THEN** it is silently skipped

### Requirement: Deduplicate commits across repos
The collector SHALL track seen SHAs and skip duplicate commits. This handles repos that share commits (e.g., forks, submodules).

#### Scenario: Same commit in two repos
- **WHEN** two configured repos contain a commit with the same SHA
- **THEN** only the first occurrence is emitted

### Requirement: Author filtering
The collector SHALL read the repo's `git config user.name` and use it as `--author` filter. If `user.name` is not configured, it SHALL collect all commits without author filter.

#### Scenario: Repo without user.name
- **WHEN** a repo has no `user.name` configured
- **THEN** all commits for the date are collected regardless of author

