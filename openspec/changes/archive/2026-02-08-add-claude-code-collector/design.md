## Context

Daily-log has 3 collectors (github, shortcut, git_local) that return events in a unified format. Claude Code stores all user messages in `~/.claude/history.jsonl` — one JSON object per line with `display`, `timestamp`, `project`, and `sessionId`. This file is lightweight (~200KB for 783 entries across 12 days) and contains only the user's side of conversations.

## Goals / Non-Goals

**Goals:**
- Add a collector that reads `history.jsonl` and emits `claude_session` events
- Group messages by `sessionId` + `project` to produce one event per session-project pair
- Provide time anchors: start time, end time, project, first message as title, message count
- Support all projects (not just the one running daily-log)

**Non-Goals:**
- Parsing full session transcripts (`projects/<path>/<sessionId>.jsonl`) — too heavy, not needed
- Summarizing or classifying sessions — the AI summarizer handles that
- Sending conversation content to the API — only titles and metadata

## Decisions

### Read only `history.jsonl`, not session files
Session JSONL files are 100KB-3MB each and contain full transcripts. `history.jsonl` is a single file with all the data we need (timestamp, project, session, first message). No need to open multiple heavy files.

**Alternative**: Parse session files for tool usage stats (files edited, commands run). Rejected for now — adds complexity and performance cost for marginal value. Can be added later.

### Group by `sessionId` + `project`
A session already maps to one project in practice, but using both fields as the group key is defensive. The first user message (excluding `/commands` and `exit`) becomes the title.

**Alternative**: Group by time gaps (>30min = new group). Rejected — sessionId already captures this naturally since each `claude` invocation gets a new session.

### Title from first meaningful message
Skip messages that are just commands (`/init`, `/mcp`, `exit`, `pwd`) or very short (`< 5 chars`). Take the first real message, truncated to 80 chars.

### Config: `claude_history_path`
Default: `~/.claude/history.jsonl`. Configurable for non-standard installs. No token needed — it's a local file.

### Simplify project paths
Strip `/Users/<username>/projects/` prefix from project paths to show clean names like `founderz`, `personal/ia/daily-log`.

## Risks / Trade-offs

- **[File not found]** → Return skipped status. User may not have Claude Code installed.
- **[Large history file]** → File grows indefinitely. We filter by date early (compare timestamp), so only matching lines are kept in memory. A 10K-line file parses in <100ms.
- **[Privacy]** → First message text goes into the report (and potentially to Claude API for summarization). This is acceptable since the user controls their own report. Title is truncated to 80 chars.
- **[Timestamp timezone]** → `history.jsonl` uses millisecond epoch timestamps. Convert to local timezone ISO 8601 to match other collectors.
