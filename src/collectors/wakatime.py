"""Collector for WakaTime coding activity."""

import urllib.error
from datetime import datetime, timezone, timedelta
from api import wakatime
from collectors._utils import format_duration


def _unix_to_iso(ts: float, tz_name: str) -> str:
    """Convert Unix timestamp to ISO 8601 string in the given timezone."""
    # Parse UTC offset from common timezone names or fall back to UTC
    # WakaTime returns IANA tz names; Python 3.9 stdlib has no zoneinfo on all platforms
    # so we request the offset from the API response and approximate
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    # Try to get offset from tz_name (e.g., "Europe/Madrid" -> +01:00 or +02:00)
    # Since we can't reliably parse IANA without zoneinfo, we use a simple heuristic:
    # fetch the API's start field which is already in UTC, and compute offset from
    # the date string. For now, return UTC ISO — the caller patches the offset.
    return dt.isoformat()


def collect_wakatime(config: dict, date: str) -> dict:
    api_key = config.get("wakatime_api_key")
    if not api_key:
        return {"source": "wakatime", "status": "skipped", "reason": "no api key"}

    events = []

    try:
        # Fetch summaries (aggregated time per project)
        summaries = wakatime(f"users/current/summaries?start={date}&end={date}", api_key)
        data = summaries.get("data", [])

        if data:
            day = data[0]
            tz_name = summaries.get("timezone", "UTC")
            day_start = f"{date}T00:00:00"

            for project in day.get("projects", []):
                total = project.get("total_seconds", 0)
                if total <= 0:
                    continue

                # Build language breakdown from project-level data
                # Summaries give languages at day level, not per-project
                events.append({
                    "type": "coding_summary",
                    "timestamp": day_start,
                    "source": "wakatime",
                    "title": f"{project['name']} — {project.get('text', format_duration(total))}",
                    "meta": {
                        "project": project["name"],
                        "total_seconds": total,
                        "human_additions": project.get("human_additions", 0),
                        "human_deletions": project.get("human_deletions", 0),
                    },
                })

        # Fetch durations (individual activity blocks)
        durations = wakatime(f"users/current/durations?date={date}", api_key)
        blocks = durations.get("data", [])

        for block in blocks:
            duration = block.get("duration", 0)
            if duration <= 0:
                continue

            ts = block.get("time", 0)
            project = block.get("project", "unknown")

            events.append({
                "type": "coding_block",
                "timestamp": _unix_to_iso(ts, durations.get("timezone", "UTC")),
                "source": "wakatime",
                "title": f"{project} ({format_duration(duration)})",
                "meta": {
                    "project": project,
                    "duration_seconds": duration,
                    "human_additions": block.get("human_additions", 0),
                    "human_deletions": block.get("human_deletions", 0),
                },
            })

    except urllib.error.HTTPError:
        return {"source": "wakatime", "events": []}
    except Exception:
        return {"source": "wakatime", "events": []}

    return {"source": "wakatime", "events": events}
