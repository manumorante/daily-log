## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Build sha-to-branch map per repo
The collector SHALL run `git log --all --format=%h|%D` once per repo to build a map from SHA to branch name. For each entry, it SHALL parse `%D` (comma-separated refs), skip `HEAD ->` prefixes and `origin/` remote refs, and use the first remaining ref as the branch. For commits not at any branch tip, it SHALL fall back to `git branch --contains <sha>` and pick the first non-main, non-master branch.

#### Scenario: Map building with mixed refs
- **WHEN** `git log --all --format=%h|%D` outputs `abc1234|HEAD -> feat/sc-42, origin/feat/sc-42, main`
- **THEN** the map entry for `abc1234` is `feat/sc-42`

#### Scenario: Commit with empty %D
- **WHEN** a commit has empty `%D` (not at any branch tip)
- **THEN** the collector runs `git branch --contains <sha>` and uses the first non-main branch
