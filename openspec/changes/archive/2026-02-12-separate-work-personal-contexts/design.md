## Context

Currently, daily-log generates a single markdown report mixing all activities (personal and Founderz work) in `~/daily-log/reports/YYYY/MM/YYYY-MM-DD.md`. Each collector returns events without context classification, making it impossible to separate work from personal activities without manual review.

The infrastructure for separation already exists (2 GitHub accounts, separate directory paths), but the tool doesn't leverage it.

## Goals / Non-Goals

**Goals:**
- Generate two independent reports: `work/` and `personal/`
- Add `context` field to all events for filtering
- Maintain backward compatibility for config (no breaking config changes)
- Keep collector logic simple and autonomous
- Add context selection to the interactive menu

**Non-Goals:**
- Config file restructuring (collectors auto-detect from existing data)
- Migrating or cleaning up old reports (zero effort — just ignored, delete manually if desired)
- Supporting mixed-context events (each event has exactly one context)
- Re-enabling Claude Code collector (deferred to future work)

## Decisions

### 1. Event Context Detection: Decentralized (per-collector)

**Decision**: Each collector implements its own context detection logic based on event data.

**Rationale**:
- Collectors already have all the data needed (username, path, project name)
- Keeps detection logic close to the data source
- No need for a centralized "context detector" service
- Each collector has unique detection rules

**Implementation**:
```python
from src.context import WORK_GITHUB_USERNAME

def collect_github(config, date):
    # ... fetch events ...
    for event in events:
        event["context"] = "work" if username == WORK_GITHUB_USERNAME else "personal"
```

**Alternatives considered**:
- Centralized context detector → Rejected: Would require passing raw data through, adding complexity
- Config-based mapping → Rejected: Redundant with existing data patterns

### 2. Report Generation: Filter After Collection

**Decision**: Collect all events first, then filter by context and generate two separate reports.

**Architecture**:
```
Collectors → All Events → Filter by context → Two Reports
                           ├─ work events → work/YYYY/MM/DD.md
                           └─ personal events → personal/YYYY/MM/DD.md
```

**Rationale**:
- Simple aggregation logic
- Easy to filter by context from the interactive menu
- Single source of truth for event collection

**Implementation in `daily_log.py`**:
```python
all_events = []
for collector_name, collector_fn in collectors.ALL:
    result = collector_fn(config, date)
    all_events.extend(result.get("events", []))

# Filter by context
work_events = [e for e in all_events if e.get("context") == "work"]
personal_events = [e for e in all_events if e.get("context") == "personal"]

# Generate reports based on selected context
if context in ("both", "work"):
    write_report(work_events, f"work/{year}/{month}/{date}.md")
if context in ("both", "personal"):
    write_report(personal_events, f"personal/{year}/{month}/{date}.md")
```

### 3. Directory Structure: Flat Context Separation

**Decision**: Reports organized as `reports/{context}/YYYY/MM/YYYY-MM-DD.md`

**Structure**:
```
~/daily-log/reports/
├── work/
│   └── 2026/
│       └── 02/
│           └── 2026-02-12.md
└── personal/
    └── 2026/
        └── 02/
            └── 2026-02-12.md
```

**Rationale**:
- Clear separation at the top level
- Easy to browse work-only or personal-only activity
- Maintains year/month hierarchy for organization
- Simple to implement (change base path)

**Alternatives considered**:
- `reports/YYYY/MM/{work,personal}-YYYY-MM-DD.md` → Rejected: Harder to browse by context
- Single report with sections → Rejected: Still mixed, not truly separated

### 4. Config Schema: No Breaking Changes

**Decision**: Keep config unchanged. Collectors auto-detect context from existing fields.

**Current config works as-is**:
```json
{
  "github_token": "...",
  "github_username": "manumorante",  // collectors check both accounts
  "shortcut_token": "...",
  "wakatime_api_key": "...",
  "anthropic_api_key": "..."
}
```

**Detection rules**:
- Git Local: Check path against known patterns
- GitHub: Check username in API response
- Shortcut: Always "work"
- WakaTime: Check project name against known keywords

**Rationale**:
- No migration required
- Collectors are smart enough to detect from data
- Avoids breaking existing setups

### 5. Context Detection Constants: Single Source of Truth

**Decision**: Define all detection patterns as constants in one module. Collectors import from there.

**Implementation**:
```python
# src/context.py
WORK_GITHUB_USERNAME = "manumorante-fdz"
WORK_PATH_PATTERNS = ["founderz/"]
WORK_PROJECT_KEYWORDS = ["founderz"]
WORK_ONLY_SOURCES = ["shortcut"]
```

**Rationale**:
- Single place to update if patterns change
- Collectors stay clean — they import constants, not define them
- Easy to review what qualifies as "work"

### 6. Interactive Menu: Add Context Selection Step

**Decision**: After date selection, prompt for context (work / personal / both).

**Flow**:
```
Menu:
1. Generate report for a specific date
   → Prompt: Select date
   → Prompt: Select context (work / personal / both)
   → Generate filtered report(s)

2. Generate report for today
   → Prompt: Select context (work / personal / both)
   → Generate filtered report(s)
```

**Rationale**:
- Gives users fine-grained control
- Avoids generating unnecessary reports
- Consistent with the interactive menu UX (no flags to remember)

### 7. Claude Code Collector: Disable

**Decision**: Comment out Claude Code collector in `collectors/__init__.py`.

**Rationale**:
- Context detection is ambiguous (working directory can be misleading)
- Not critical for MVP (other collectors cover core activity)
- Can be re-enabled later with better heuristics or manual classification

```python
# from .claude_code import collect_claude_code

ALL = [
    ("GitHub", collect_github),
    ("Shortcut", collect_shortcut),
    ("Git Local", collect_git_local),
    ("WakaTime", collect_wakatime),
    # ("Claude Code", collect_claude_code),  # Disabled: ambiguous context
]
```

## Risks / Trade-offs

**[Risk] Events missing context field** → Default to "personal" if undefined, log warning.

**[Risk] Detection patterns scattered across collectors** → Mitigation: Define constants in a single place (e.g. `WORK_GITHUB_USERNAME`, `WORK_PATH_PATTERNS`, `WORK_PROJECT_KEYWORDS`) so changes only require updating one location.

**[Trade-off] Old reports not migrated** → Zero effort: no migration code, no cleanup logic. Old reports in `reports/YYYY/MM/` are simply ignored.

## Migration Plan

**Deployment**:
1. Update all collectors to add `context` field
2. Update `daily_log.py` to filter and generate two reports
3. Update interactive menu to prompt for context selection
4. Disable Claude Code collector
5. Test with a sample date to verify both reports generate correctly

**Rollback**:
- If issues arise, can revert code changes and continue using old structure
- No data loss risk

**User Communication**:
- Reports now generate in `work/` and `personal/` subdirectories
- The interactive menu prompts for context selection before generating
- Old reports in `reports/YYYY/MM/` are simply ignored (no migration, no cleanup — delete manually if desired)
