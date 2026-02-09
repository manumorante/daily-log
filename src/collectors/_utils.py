"""Shared utilities for collectors."""

import re

_SC_PATTERN = re.compile(r"sc-(\d+)", re.IGNORECASE)


def extract_task_id(branch):
    """Extract Shortcut story ID from branch name matching sc-XXXX pattern."""
    if not branch:
        return None
    m = _SC_PATTERN.search(branch)
    return m.group(1) if m else None
