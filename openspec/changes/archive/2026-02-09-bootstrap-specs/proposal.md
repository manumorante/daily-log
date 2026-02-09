## Why

The project adopted OpenSpec mid-development. Only capabilities added after adoption have specs (4 out of ~13). When a future change touches an unspecified area, the agent must read raw code to infer intent — slow and error-prone. A lightweight bootstrap pass creates minimal specs for all existing capabilities, giving OpenSpec a complete map of the system.

## What Changes

- Create minimal specs for every existing capability that lacks one
- Each spec covers: responsibility, input/output contract, key behaviors, edge cases
- No code changes — this is documentation only
- Existing specs remain untouched

## Capabilities

### New Capabilities

- `github-collector`: Collect commits, PRs, issues, and reviews from GitHub Events API
- `shortcut-collector`: Collect stories and epics from Shortcut API, filtered by member
- `git-local-collector`: Collect commits from local git repos, filtered by author
- `api-helpers`: HTTP utility functions for authenticated API calls (fetch, github, shortcut, wakatime)
- `config-system`: Load, merge, and validate configuration from file and environment variables
- `report-output`: Render markdown reports and save with embedded raw data; skip if unchanged
- `cli`: Command-line interface, argument parsing, and main orchestration loop
- `terminal-ui`: Pastel ANSI 256 color and Unicode symbol helpers for terminal output
- `setup-wizard`: Interactive CLI for configuring all data sources

### Modified Capabilities

(none — existing specs are not changed)

## Impact

- No code changes
- Adds 9 new spec files under `openspec/specs/`
- Future changes to any area will have spec context available
