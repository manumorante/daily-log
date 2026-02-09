"""Shared utilities for collectors."""

import re

_SC_PATTERN = re.compile(r"sc-(\d+)", re.IGNORECASE)


def extract_task_id(branch):
    """Extract Shortcut story ID from branch name matching sc-XXXX pattern."""
    if not branch:
        return None
    m = _SC_PATTERN.search(branch)
    return m.group(1) if m else None


def format_duration(seconds):
    # type: (float) -> str
    """Format seconds into a human-readable string like '1h 30min'."""
    hours = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {mins}min"
    return f"{mins}min"


def branch_meta(branch):
    # type: (str) -> dict
    """Build branch and task_id meta entries from a branch name."""
    meta = {}
    if branch:
        meta["branch"] = branch
        tid = extract_task_id(branch)
        if tid:
            meta["task_id"] = tid
    return meta
