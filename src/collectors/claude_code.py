"""Collector for Claude Code session activity."""

import json
import os
from datetime import datetime, timezone
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
            },
        })

    # Sort events by timestamp
    events.sort(key=lambda e: e["timestamp"])

    return {"source": "claude_code", "events": events}
