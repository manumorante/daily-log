"""Time estimation engine — groups events by task and estimates time spent."""

from datetime import datetime, timedelta, timezone
from typing import Optional

# Events to skip during task grouping — attributed separately
_SKIP_TYPES = {"coding_summary", "coding_block", "claude_session"}

# Gap thresholds
_REPO_SPLIT_GAP = timedelta(minutes=60)
_SESSION_GAP = timedelta(minutes=30)

# Margin around task windows for coding_block attribution
_WINDOW_MARGIN = timedelta(minutes=15)


def _parse_ts(ts_str):
    # type: (str) -> Optional[datetime]
    """Parse an ISO 8601 timestamp string into a UTC datetime."""
    if not ts_str:
        return None
    try:
        # Python 3.9: fromisoformat doesn't handle Z suffix
        ts_str = ts_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts_str)
        # Normalize to UTC for consistent comparison
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc)
        else:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _repo_name(value):
    # type: (str) -> str
    """Extract last path component as normalized repo name."""
    if not value:
        return ""
    return value.rstrip("/").rsplit("/", 1)[-1].lower()


def _group_events(events):
    # type: (list) -> dict
    """Group events into task buckets. Returns {task_id: [events]}."""
    by_task_id = {}  # explicit task_id
    by_repo = {}     # repo-based fallback
    other = []       # catch-all

    for ev in events:
        ev_type = ev.get("type", "")
        if ev_type in _SKIP_TYPES:
            continue

        meta = ev.get("meta", {})
        task_id = meta.get("task_id")

        if task_id:
            by_task_id.setdefault(task_id, []).append(ev)
        else:
            repo = _repo_name(meta.get("repo", "")) or _repo_name(meta.get("project", ""))
            if repo:
                by_repo.setdefault(repo, []).append(ev)
            else:
                other.append(ev)

    # Temporal splitting within repo groups
    groups = {}

    for task_id, evts in by_task_id.items():
        groups[task_id] = evts

    for repo, evts in by_repo.items():
        splits = _split_by_time(evts, _REPO_SPLIT_GAP)
        if len(splits) == 1:
            groups["repo:" + repo] = splits[0]
        else:
            for i, chunk in enumerate(splits, 1):
                groups["repo:{}:{}".format(repo, i)] = chunk

    if other:
        groups["other"] = other

    return groups


def _sort_by_ts(events):
    # type: (list) -> list
    """Sort events by parsed timestamp (handles mixed timezones)."""
    # Use a large fallback so events without timestamps sort last
    epoch = datetime(2000, 1, 1, tzinfo=timezone.utc)
    return sorted(events, key=lambda e: _parse_ts(e.get("timestamp", "")) or epoch)


def _split_by_time(events, gap):
    # type: (list, timedelta) -> list
    """Split events into chunks where consecutive events are > gap apart."""
    if not events:
        return []

    sorted_evts = _sort_by_ts(events)
    chunks = [[sorted_evts[0]]]

    for ev in sorted_evts[1:]:
        prev_ts = _parse_ts(chunks[-1][-1].get("timestamp", ""))
        curr_ts = _parse_ts(ev.get("timestamp", ""))
        if prev_ts and curr_ts and (curr_ts - prev_ts) > gap:
            chunks.append([ev])
        else:
            chunks[-1].append(ev)

    return chunks


def _build_time_window(events):
    # type: (list) -> tuple
    """Return (start_dt, end_dt, project_name) for a task's events."""
    timestamps = []
    project = ""

    for ev in events:
        ts = _parse_ts(ev.get("timestamp", ""))
        if ts:
            timestamps.append(ts)
        meta = ev.get("meta", {})
        if not project:
            project = _repo_name(meta.get("repo", "")) or _repo_name(meta.get("project", ""))

    if not timestamps:
        return None, None, project

    start = min(timestamps) - _WINDOW_MARGIN
    end = max(timestamps) + _WINDOW_MARGIN
    return start, end, project


def _attribute_coding_blocks(all_events, task_windows):
    # type: (list, dict) -> dict
    """Attribute coding_block events to tasks. Returns {task_id: total_seconds}."""
    blocks = [ev for ev in all_events if ev.get("type") == "coding_block"]
    attribution = {tid: 0.0 for tid in task_windows}

    for block in blocks:
        meta = block.get("meta", {})
        block_ts = _parse_ts(block.get("timestamp", ""))
        block_project = _repo_name(meta.get("project", ""))
        duration = meta.get("duration_seconds", 0)

        if not block_ts or not block_project or duration <= 0:
            continue

        # Find matching tasks
        matches = []
        for tid, (start, end, project) in task_windows.items():
            if start is None or end is None:
                continue
            if project == block_project and start <= block_ts <= end:
                matches.append(tid)

        if len(matches) == 1:
            attribution[matches[0]] += duration
        elif len(matches) > 1:
            # Split proportionally
            share = duration / len(matches)
            for tid in matches:
                attribution[tid] += share

    return attribution


def _attribute_sessions(all_events, task_windows):
    # type: (list, dict) -> dict
    """Attribute claude_session events to tasks. Returns {task_id: total_seconds}."""
    sessions = [ev for ev in all_events if ev.get("type") == "claude_session"]
    attribution = {tid: 0.0 for tid in task_windows}

    for session in sessions:
        meta = session.get("meta", {})
        session_project = _repo_name(meta.get("project", ""))
        start_ts = _parse_ts(session.get("timestamp", ""))
        end_ts = _parse_ts(meta.get("end_time", ""))

        if not session_project or not start_ts or not end_ts:
            continue

        # Use active_seconds (gap-aware) if available, fall back to full span
        duration = meta.get("active_seconds", 0)
        if not duration:
            duration = (end_ts - start_ts).total_seconds()
        if duration <= 0:
            continue

        # Match by project name AND temporal overlap with task window
        matches = []
        for tid, (ws, we, proj) in task_windows.items():
            if ws is None or we is None:
                continue
            if proj == session_project and start_ts <= we and end_ts >= ws:
                matches.append(tid)

        # Fallback: match by project name only if no temporal match
        if not matches:
            matches = [
                tid for tid, (s, e, proj) in task_windows.items()
                if proj == session_project
            ]

        if len(matches) == 1:
            attribution[matches[0]] += duration
        elif len(matches) > 1:
            share = duration / len(matches)
            for tid in matches:
                attribution[tid] += share

    return attribution


def _detect_sessions(events):
    # type: (list) -> list
    """Detect work sessions within a task's events. Returns list of session dicts."""
    if not events:
        return []

    sorted_evts = _sort_by_ts(events)
    sessions = []
    current = [sorted_evts[0]]

    for ev in sorted_evts[1:]:
        prev_ts = _parse_ts(current[-1].get("timestamp", ""))
        curr_ts = _parse_ts(ev.get("timestamp", ""))
        if prev_ts and curr_ts and (curr_ts - prev_ts) > _SESSION_GAP:
            sessions.append(current)
            current = [ev]
        else:
            current.append(ev)

    sessions.append(current)

    result = []
    for chunk in sessions:
        start = _parse_ts(chunk[0].get("timestamp", ""))
        end = _parse_ts(chunk[-1].get("timestamp", ""))
        if start and end:
            result.append({
                "start": chunk[0]["timestamp"],
                "end": chunk[-1]["timestamp"],
                "duration_seconds": (end - start).total_seconds(),
            })

    return result


def _generate_label(task_id, events):
    # type: (str, list) -> str
    """Generate a human-readable label for a task."""
    if task_id == "other":
        return "Other activity"

    if task_id.startswith("repo:"):
        # Extract repo name (strip "repo:" prefix and optional ":N" suffix)
        parts = task_id.split(":")
        return parts[1] if len(parts) >= 2 else task_id

    # Shortcut task_id — look for a story event title
    for ev in events:
        if ev.get("type") == "story":
            title = ev.get("title", "")
            if title:
                return title

    return "sc-{}".format(task_id)


def estimate_tasks(events):
    # type: (list) -> list
    """Take a flat list of events and return tasks with time estimates."""
    if not events:
        return []

    # Step 1: Group events by task
    groups = _group_events(events)

    if not groups:
        return []

    # Step 2: Build time windows for coding_block attribution
    task_windows = {}
    for tid, evts in groups.items():
        start, end, project = _build_time_window(evts)
        task_windows[tid] = (start, end, project)

    # Step 3: Attribute WakaTime coding_blocks and Claude sessions
    coding_time = _attribute_coding_blocks(events, task_windows)
    session_time = _attribute_sessions(events, task_windows)

    # Step 4: Build task output
    tasks = []
    for tid, evts in groups.items():
        sorted_evts = _sort_by_ts(evts)
        first_ts = _parse_ts(sorted_evts[0].get("timestamp", "")) if sorted_evts else None
        last_ts = _parse_ts(sorted_evts[-1].get("timestamp", "")) if sorted_evts else None
        window_secs = (last_ts - first_ts).total_seconds() if first_ts and last_ts else 0

        sources = sorted(set(ev.get("source", "") for ev in evts if ev.get("source")))

        tasks.append({
            "task_id": tid,
            "label": _generate_label(tid, evts),
            "events": evts,
            "coding_time_seconds": coding_time.get(tid, 0),
            "session_time_seconds": session_time.get(tid, 0),
            "window_seconds": window_secs,
            "sessions": _detect_sessions(evts),
            "sources": sources,
        })

    # Sort: tasks with most coding time first, then by window
    tasks.sort(key=lambda t: (t["coding_time_seconds"], t["window_seconds"]), reverse=True)

    return tasks
