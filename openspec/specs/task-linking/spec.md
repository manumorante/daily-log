# task-linking Specification

## Purpose
Model for associating events with tasks. Defines task_id field, linking signals (branch-based, repo-based, temporal), and grouping rules for future time estimation.

## Requirements
### Requirement: task_id extraction from branch name
Collectors that have access to a branch name SHALL extract `task_id` by matching the regex `sc-(\d+)` against the branch name. The captured group is the Shortcut story ID. If no match, `task_id` SHALL be omitted from `meta` (not set to null).

#### Scenario: Branch with sc-XXXX pattern
- **WHEN** a commit or PR has branch `feat/sc-1234-add-login`
- **THEN** `meta.task_id` is `"1234"`

#### Scenario: Branch without sc-XXXX pattern
- **WHEN** a commit has branch `fix-typo-readme`
- **THEN** `meta.task_id` is absent from the event

#### Scenario: Shortcut story event
- **WHEN** shortcut collector emits a story event with `meta.id` = 2983
- **THEN** `meta.task_id` is `"2983"` (string, matching the branch-derived format)

### Requirement: Task-linking priority model
Events SHALL be linkable to tasks using this priority:
1. **Explicit `task_id`** — from `sc-(\d+)` in branch name or Shortcut story ID
2. **Repo-based grouping** — events without `task_id` grouped by `meta.repo` or `meta.project`
3. **Temporal proximity** — events within 30 minutes of each other likely belong to the same work session

This model is documented for future implementation. This change does NOT implement grouping or session detection.

#### Scenario: Two commits with same task_id
- **WHEN** two commits have `meta.task_id` = "1234" from branch `feat/sc-1234-login`
- **THEN** the future grouping layer links them to the same task

#### Scenario: Events without task_id in same repo
- **WHEN** three commits have no `task_id` but share `meta.repo` = "daily-log"
- **THEN** the future grouping layer groups them by repo

#### Scenario: Events close in time
- **WHEN** a commit at 14:00 and a PR at 14:20 share no `task_id` or repo
- **THEN** the future grouping layer may link them by temporal proximity (within 30min)
