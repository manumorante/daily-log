"""Collector for Claude Code session activity."""

import json
import os
from datetime import datetime
from pathlib import Path


def _simplify_project(project_path):
    """Strip home dir and projects/ prefix from project path."""
    home = os.path.expanduser("~")
    path = project_path
    if path.startswith(home):
        path = path[len(home):]
    # Remove leading /
    path = path.lstrip("/")
    # Strip projects/ prefix if present
    if path.startswith("projects/"):
        path = path[len("projects/"):]
    return path or project_path


def _extract_title(messages):
    """Get first meaningful message as title, skipping commands and noise."""
    for msg in messages:
        display = msg.get("display", "").strip()
        if not display:
            continue
        if display.startswith("/"):
            continue
        if display.lower() in ("exit", "pwd"):
            continue
        if len(display) < 5:
            continue
        return display[:80]
    return "Claude Code session"


# If gap between consecutive messages exceeds this, the time is idle
_IDLE_THRESHOLD_MS = 10 * 60 * 1000  # 10 minutes

# Reading margin per message (accounts for reading Claude's response)
_READ_MARGIN_MS = 2 * 60 * 1000  # 2 minutes


def _calc_active_seconds(entries):
    """Calculate active time from message timestamps, excluding idle gaps."""
    if len(entries) < 2:
        return _READ_MARGIN_MS / 1000  # single message = just the read margin

    active_ms = 0
    for i in range(1, len(entries)):
        gap = entries[i].get("timestamp", 0) - entries[i - 1].get("timestamp", 0)
        if gap <= _IDLE_THRESHOLD_MS:
            active_ms += gap
        # Idle gaps are simply not counted

    # Add read margin for the last message (you read Claude's final response)
    active_ms += _READ_MARGIN_MS

    return active_ms / 1000


def collect_claude_code(config, date):
    """Collect Claude Code sessions from history.jsonl."""
    history_path = config.get("claude_history_path", "~/.claude/history.jsonl")
    history_path = Path(os.path.expanduser(history_path))

    if not history_path.exists():
        return {"source": "claude_code", "status": "skipped", "reason": "history file not found"}

    # Parse entries for the requested date
    groups = {}  # (sessionId, project) -> [entries]

    try:
        with open(history_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                ts_ms = entry.get("timestamp")
                if not ts_ms:
                    continue

                # Convert ms epoch to local datetime
                dt = datetime.fromtimestamp(ts_ms / 1000)
                if dt.strftime("%Y-%m-%d") != date:
                    continue

                session_id = entry.get("sessionId", "")
                project = entry.get("project", "")
                if not session_id:
                    continue

                key = (session_id, project)
                if key not in groups:
                    groups[key] = []
                groups[key].append(entry)

    except Exception:
        return {"source": "claude_code", "status": "skipped", "reason": "error reading history"}

    # Build events from groups
    events = []
    for (session_id, project), entries in groups.items():
        # Sort by timestamp
        entries.sort(key=lambda e: e.get("timestamp", 0))

        ts_start = entries[0].get("timestamp", 0)
        ts_end = entries[-1].get("timestamp", 0)

        dt_start = datetime.fromtimestamp(ts_start / 1000).astimezone()
        dt_end = datetime.fromtimestamp(ts_end / 1000).astimezone()

        events.append({
            "type": "claude_session",
            "timestamp": dt_start.isoformat(),
            "source": "claude_code",
            "title": _extract_title(entries),
            "meta": {
                "project": _simplify_project(project),
                "session_id": session_id[:8],
                "message_count": len(entries),
                "end_time": dt_end.isoformat(),
                "active_seconds": _calc_active_seconds(entries),
            },
        })

    # Sort events by timestamp
    events.sort(key=lambda e: e["timestamp"])

    return {"source": "claude_code", "events": events}
