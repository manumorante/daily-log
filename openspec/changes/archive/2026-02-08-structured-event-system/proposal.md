## Why

Collectors return ad-hoc structures without timestamps (commits without time, stories without change date). This prevents analyzing temporal patterns like work sessions, bottlenecks or trends. The summarizer receives plain markdown from Claude, making it impossible to display parts of the summary independently (e.g., only the highlight in terminal).

## What Changes

- Enrich collectors with timestamps on every data point (commit time, story/epic change time)
- Unify all collector output into a standard event format with common fields
- Change Claude prompt to return structured JSON instead of markdown
- Render output (terminal, .md file) from the JSON, not from plain text

## Capabilities

### New Capabilities
- `event-format`: Standard event format with common fields (type, timestamp, source, title, meta). All collectors emit events in this format.
- `json-summarizer`: Claude receives events and returns structured JSON (highlight, code groups, tasks, patterns, risks) instead of plain markdown.

### Modified Capabilities

## Impact

- `src/collectors/github.py`: Add timestamps to commits and events
- `src/collectors/shortcut.py`: Add change timestamps to stories and epics
- `src/collectors/git_local.py`: Add commit time (already available in git log)
- `src/daily_log.py`: Change prompt, parse Claude JSON, new render for terminal and file
- `src/daily_log.py`: `_fallback_summary` must adapt to the new event format
