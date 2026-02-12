"""Collector for Shortcut stories and epics."""

import urllib.parse
from api import shortcut


def _resolve_member_id(config: dict, token: str) -> str:
    """Get member_id from config or auto-detect from API."""
    mid = config.get("shortcut_member_id", "")
    if mid:
        return mid
    try:
        me = shortcut("member", token)
        return me.get("id", "")
    except Exception:
        return ""


def _member_changes(story_id: int, member_id: str, date: str, token: str) -> list:
    """Return list of changed_at timestamps for this member on the given date."""
    timestamps = []
    try:
        history = shortcut(f"stories/{story_id}/history", token)
        for entry in history:
            if entry.get("member_id") == member_id and entry.get("changed_at", "")[:10] == date:
                timestamps.append(entry["changed_at"])
    except Exception:
        pass
    return timestamps


def collect_shortcut(config: dict, date: str) -> dict:
    token = config.get("shortcut_token")
    if not token:
        return {"source": "shortcut", "status": "skipped", "reason": "no token"}

    member_id = _resolve_member_id(config, token)
    events = []

    try:
        # State map (id -> name)
        state_map = {}
        for wf in shortcut("workflows", token):
            for s in wf.get("states", []):
                state_map[s["id"]] = s["name"]

        # Stories updated today
        query = urllib.parse.quote(f"updated:{date}")
        data = shortcut(f"search/stories?query={query}", token)

        for story in data.get("data", []):
            story_id = story.get("id")

            # Filter: only stories this member touched
            if member_id:
                changes = _member_changes(story_id, member_id, date, token)
                if not changes:
                    continue
                ts = changes[0]
            else:
                ts = story.get("updated_at", "")

            state_id = story.get("workflow_state_id")
            completed = story.get("completed") and story.get("completed_at", "")[:10] == date

            events.append({
                "type": "story",
                "timestamp": ts,
                "source": "shortcut",
                "context": "work",
                "title": story.get("name", ""),
                "meta": {
                    "id": story_id,
                    "task_id": str(story_id),
                    "story_type": story.get("story_type", ""),
                    "workflow_state": state_map.get(state_id, str(state_id) if state_id else "unknown"),
                    "completed": completed,
                },
            })

        # Epics updated today
        epic_query = urllib.parse.quote(f"updated:{date}")
        epic_data = shortcut(f"search/epics?query={epic_query}", token)

        for epic in epic_data.get("data", []):
            events.append({
                "type": "epic",
                "timestamp": epic.get("updated_at", ""),
                "source": "shortcut",
                "context": "work",
                "title": epic.get("name", ""),
                "meta": {
                    "id": epic.get("id"),
                    "state": epic.get("state", ""),
                },
            })

    except Exception as e:
        return {"source": "shortcut", "events": [], "error": str(e)}

    return {"source": "shortcut", "events": events}
