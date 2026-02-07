"""Collector de stories y epics en Shortcut."""

import urllib.parse
from api import shortcut


def _member_touched_story(story_id: int, member_id: str, date: str, token: str) -> bool:
    """Comprueba si el member hizo algun cambio en la story en la fecha dada."""
    try:
        history = shortcut(f"stories/{story_id}/history", token)
        for entry in history:
            if entry.get("member_id") == member_id and entry.get("changed_at", "")[:10] == date:
                return True
    except Exception:
        pass
    return False


def _resolve_member_id(config: dict, token: str) -> str:
    """Obtiene el member_id del config o lo autodetecta desde la API."""
    mid = config.get("shortcut_member_id", "")
    if mid:
        return mid
    try:
        me = shortcut("member", token)
        return me.get("id", "")
    except Exception:
        return ""


def collect_shortcut(config: dict, date: str) -> dict:
    token = config.get("shortcut_token")
    if not token:
        return {"source": "shortcut", "status": "skipped", "reason": "no token"}

    member_id = _resolve_member_id(config, token)
    results = {"source": "shortcut", "stories_updated": [], "stories_completed": [], "epics_updated": []}

    try:
        # Mapa de estados (id -> nombre)
        state_map = {}
        for wf in shortcut("workflows", token):
            for s in wf.get("states", []):
                state_map[s["id"]] = s["name"]

        # Stories actualizadas hoy (todas)
        query = urllib.parse.quote(f"updated:{date}")
        data = shortcut(f"search/stories?query={query}", token)

        for story in data.get("data", []):
            story_id = story.get("id")

            # Filtrar: solo stories que yo toque
            if member_id and not _member_touched_story(story_id, member_id, date, token):
                continue

            state_id = story.get("workflow_state_id")
            info = {
                "id": story_id,
                "name": story.get("name", ""),
                "type": story.get("story_type", ""),
                "workflow_state": state_map.get(state_id, str(state_id) if state_id else "unknown"),
            }

            if story.get("completed") and story.get("completed_at", "")[:10] == date:
                results["stories_completed"].append(info)
            else:
                results["stories_updated"].append(info)

        # Epics actualizados hoy
        epic_query = urllib.parse.quote(f"updated:{date}")
        epic_data = shortcut(f"search/epics?query={epic_query}", token)

        for epic in epic_data.get("data", []):
            results["epics_updated"].append({
                "id": epic.get("id"),
                "name": epic.get("name", ""),
                "state": epic.get("state", ""),
            })

    except Exception as e:
        results["error"] = str(e)

    return results
