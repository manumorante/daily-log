## Why

The current daily-log generates a single report mixing personal and work (Founderz) activities, making it difficult to review each context independently. This change enables clear separation of work and personal development activity by generating two distinct reports.

## What Changes

- Generate two separate reports: `work/YYYY/MM/YYYY-MM-DD.md` and `personal/YYYY/MM/YYYY-MM-DD.md`
- Add context detection to all events (`"context": "work" | "personal"`)
- Centralize detection patterns in `src/context.py` (single source of truth for work identifiers)
- Update collectors to classify events using these constants:
  - GitHub: username match
  - Git Local: path pattern match
  - Shortcut: always work
  - WakaTime: project name keyword match
- Disable Claude Code collector (ambiguous context classification, re-enable later)
- Interactive menu adds context selection (work / personal / both) before generating a report

## Capabilities

### New Capabilities

- `context-constants`: `src/context.py` — centralized work detection patterns (usernames, paths, keywords)
- `context-detection`: Logic in each collector to classify events as work or personal using the constants above

### Modified Capabilities

- `event-format`: Add required `context` field to all events
- `report-output`: Generate two separate reports instead of one, organized in `work/` and `personal/` subdirectories
- `github-collector`: Add context detection based on username
- `git-local-collector`: Add context detection based on repository path
- `wakatime-collector`: Add context detection based on project name
- `shortcut-collector`: Always set context to "work"
- `interactive-menu`: Add context selection step (work / personal / both) when generating a report

## Impact

- **BREAKING**: Report location changes from `reports/YYYY/MM/` to `reports/{work,personal}/YYYY/MM/`. No migration, no cleanup code — old reports are simply ignored.
- Config schema remains mostly unchanged (collectors auto-detect context from existing fields)
- All existing collectors need updates to add context detection
- Claude Code collector will be disabled (commented out in `collectors/__init__.py`)
- Prepares foundation for adding Harvest collector (work-only) in the future
