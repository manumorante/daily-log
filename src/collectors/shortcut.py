"""Collector de stories en Shortcut."""

import urllib.parse
from api import shortcut


def collect_shortcut(config: dict, date: str) -> dict:
    token = config.get("shortcut_token")
    if not token:
        return {"source": "shortcut", "status": "skipped", "reason": "no token"}

    results = {"source": "shortcut", "stories_updated": [], "stories_completed": []}

    try:
        # Mapa de estados (id -> nombre)
        state_map = {}
        for wf in shortcut("workflows", token):
            for s in wf.get("states", []):
                state_map[s["id"]] = s["name"]

        # Stories actualizadas hoy
        query = urllib.parse.quote(f"updated:{date}")
        data = shortcut(f"search/stories?query={query}", token)

        for story in data.get("data", []):
            state_id = story.get("workflow_state_id")
            info = {
                "id": story.get("id"),
                "name": story.get("name", ""),
                "type": story.get("story_type", ""),
                "workflow_state": state_map.get(state_id, str(state_id) if state_id else "unknown"),
            }

            if story.get("completed") and story.get("completed_at", "")[:10] == date:
                results["stories_completed"].append(info)
            else:
                results["stories_updated"].append(info)

    except Exception as e:
        results["error"] = str(e)

    return results
