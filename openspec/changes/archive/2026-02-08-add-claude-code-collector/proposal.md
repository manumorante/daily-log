## Why

The daily report lacks temporal context about when and what the developer was working on throughout the day. Claude Code's local history (`~/.claude/history.jsonl`) contains timestamped user messages across all projects, providing natural "time anchors" that help contextualize commits, PRs, and task activity.

## What Changes

- Add a new `claude_code` collector in `src/collectors/claude_code.py`
- Register it in `src/collectors/__init__.py`
- Parse `~/.claude/history.jsonl` to extract sessions grouped by `sessionId` + `project`
- Each session group becomes a `claude_session` event with start/end time, project name, first message as title, and message count
- Add `claude_history_path` to config (defaulting to `~/.claude/history.jsonl`)

## Capabilities

### New Capabilities
- `claude-code-collector`: Collector that reads Claude Code local history and emits session events grouped by project

### Modified Capabilities
- `event-format`: Add scenario for `claude_session` event type with its expected schema

## Impact

- New file: `src/collectors/claude_code.py`
- Modified: `src/collectors/__init__.py` (register new collector)
- Modified: `src/daily_log.py` (config default for history path)
- No new dependencies (stdlib only: json, os, pathlib, datetime)
- No external API calls — reads a local file
