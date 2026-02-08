## Context

daily-log has 3 collectors (github, shortcut, git_local) that return dicts with different structures. The summarizer sends that data to Claude and gets plain markdown back. There are no timestamps, no common format, and no way to analyze anything beyond rendering text.

Current collector output:
- `github.py`: returns `{events: [{type, action, repo, title}], commits: []}`
- `shortcut.py`: returns `{stories_updated: [{id, name, type, workflow_state}], stories_completed: [...], epics_updated: [...]}`
- `git_local.py`: returns `{repos: [{name, commits: [{sha, message, author}]}]}`

## Goals / Non-Goals

**Goals:**
- All collectors emit events with the same schema (type, timestamp, source, title, meta)
- Every event has a timestamp to enable temporal analysis
- Claude returns structured JSON with separate fields (highlight, code, tasks, patterns, risks)
- Terminal shows only the highlight; .md file is rendered from the full JSON

**Non-Goals:**
- Web dashboard or visualization (future)
- Event persistence in a database
- Cross-day historical analysis (for now each run is independent)

## Decisions

### 1. Unified event format

Each collector returns a list of dicts with this schema:

```python
{
    "type": "commit" | "pr" | "review" | "issue" | "story" | "epic",
    "timestamp": "2026-02-07T14:32:00+01:00",  # ISO 8601
    "source": "github" | "shortcut" | "git_local",
    "title": "feat: add example rule in .agents/rules",
    "meta": {
        # type-specific fields
    }
}
```

Alternative considered: keep separate structures and normalize in the summarizer. Discarded because it duplicates logic and makes adding new sources harder.

### 2. Timestamps by source

- **git_local**: `git log --format=%aI` (author date ISO)
- **github**: `created_at` field from the events API
- **shortcut**: `changed_at` field from the history endpoint (already used for member filtering)

### 3. Summarizer JSON

Claude receives events and returns:

```json
{
    "highlight": "Brief paragraph of key activity",
    "code": [
        {"group": "group name", "items": ["commit description 1", "..."]}
    ],
    "tasks": [
        {"id": 2983, "name": "...", "status": "in_progress", "note": "optional"}
    ],
    "patterns": ["observation 1", "..."],
    "risks": ["risk 1", "..."]
}
```

Alternative considered: ask for highlight + full markdown. Discarded because it doesn't allow manipulating sections individually.

### 4. Render from JSON

- **Terminal**: only `highlight`
- **.md file**: render all sections from JSON
- **Fallback** (no AI): generate the same JSON with plain data (empty highlight, code/tasks directly from events)

## Risks / Trade-offs

- [Claude returns invalid JSON] → Parse with try/except, fall back to plain text response
- [More API calls for timestamps] → shortcut history is already called (for member_id filtering), github events already include timestamps, git log only changes the format string. Minimal impact.
- [Breaking change in output] → Existing reports are not touched. Only new ones use the JSON format.
