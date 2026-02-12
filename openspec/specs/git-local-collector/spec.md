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
For each repo path in `git_repos`, the collector SHALL run `git log` with `--since={date}T00:00:00 --until={date}T23:59:59 --format=%h|%s|%an|%aI --all`. It SHALL filter by the repo's configured `user.name` as `--author`. It SHALL build a sha-to-branch map by running `git log --all --format=%h|%D` once per repo, and enrich each commit event with `meta.branch` and optionally `meta.task_id`.

#### Scenario: Repo with 3 commits today
- **WHEN** a repo has 3 commits by the configured author on the requested date
- **THEN** 3 `commit` events are emitted with meta: sha, repo (basename of path), author, branch

#### Scenario: Repo path does not exist
- **WHEN** a configured repo path does not exist on disk
- **THEN** it is silently skipped

#### Scenario: Commit on feature branch with sc-XXXX
- **WHEN** a commit SHA maps to branch `feat/sc-1234-login` in the sha-to-branch map
- **THEN** the event includes `meta.branch: "feat/sc-1234-login"` and `meta.task_id: "1234"`

#### Scenario: Commit on branch without sc-XXXX
- **WHEN** a commit SHA maps to branch `fix-readme-typo`
- **THEN** the event includes `meta.branch: "fix-readme-typo"` and `meta.task_id` is absent

#### Scenario: Commit at branch tip with multiple refs
- **WHEN** `%D` for a commit is `HEAD -> feat/sc-1234-login, origin/feat/sc-1234-login`
- **THEN** the sha-to-branch map picks `feat/sc-1234-login` (first non-HEAD, non-remote ref)

#### Scenario: Commit not at any branch tip
- **WHEN** `%D` is empty for a commit and `git branch --contains <sha>` returns `feat/sc-1234-login` and `main`
- **THEN** the sha-to-branch map picks `feat/sc-1234-login` (first non-main, non-master branch)

### Requirement: Build sha-to-branch map per repo
The collector SHALL run `git log --all --format=%h|%D` once per repo to build a map from SHA to branch name. For each entry, it SHALL parse `%D` (comma-separated refs), skip `HEAD ->` prefixes and `origin/` remote refs, and use the first remaining ref as the branch. For commits not at any branch tip, it SHALL fall back to `git branch --contains <sha>` and pick the first non-main, non-master branch.

#### Scenario: Map building with mixed refs
- **WHEN** `git log --all --format=%h|%D` outputs `abc1234|HEAD -> feat/sc-42, origin/feat/sc-42, main`
- **THEN** the map entry for `abc1234` is `feat/sc-42`

#### Scenario: Commit with empty %D
- **WHEN** a commit has empty `%D` (not at any branch tip)
- **THEN** the collector runs `git branch --contains <sha>` and uses the first non-main branch

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


### Requirement: Context detection by repository path
The collector SHALL import `WORK_PATH_PATTERNS` from `src/context` and add `"context": "work"` to events if any pattern in the list appears in the repo path, otherwise `"context": "personal"`.

#### Scenario: Work repository path
- **WHEN** collecting commits from `/Users/manumorante/projects/founderz/backend`
- **THEN** all events have `"context": "work"` (path contains `"founderz/"`)

#### Scenario: Personal repository path
- **WHEN** collecting commits from `/Users/manumorante/projects/personal/daily-log`
- **THEN** all events have `"context": "personal"` (no work pattern matches)

#### Scenario: Multiple repos with mixed contexts
- **WHEN** `git_repos` config includes both `/path/to/founderz/backend` and `/path/to/personal/daily-log`
- **THEN** events from founderz repos have `"context": "work"` and events from personal repos have `"context": "personal"`
