"""Collector de actividad en GitHub."""

import urllib.error
from api import github

# Parsers por tipo de evento — {EventType: extractor(repo, payload) -> list[dict]}
_PARSERS = {
    "PushEvent": lambda repo, p: [
        {"type": "commit", "repo": repo, "sha": c.get("sha", "")[:7],
         "message": c.get("message", "").split("\n")[0]}
        for c in p.get("commits", [])
    ],
    "PullRequestEvent": lambda repo, p: [{
        "type": "PR", "action": p.get("action", ""),
        "repo": repo, "title": p.get("pull_request", {}).get("title", ""),
    }],
    "IssuesEvent": lambda repo, p: [{
        "type": "Issue", "action": p.get("action", ""),
        "repo": repo, "title": p.get("issue", {}).get("title", ""),
    }],
    "PullRequestReviewEvent": lambda repo, p: [{
        "type": "Review", "repo": repo,
        "title": p.get("pull_request", {}).get("title", ""),
    }],
}


def collect_github(config: dict, date: str) -> dict:
    token, username = config.get("github_token"), config.get("github_username")
    if not token or not username:
        return {"source": "github", "status": "skipped", "reason": "no token/username"}

    results = {"source": "github", "events": [], "commits": []}

    try:
        events = github(f"users/{username}/events?per_page=100", token)

        for event in events:
            if event.get("created_at", "")[:10] != date:
                continue

            parser = _PARSERS.get(event["type"])
            if not parser:
                continue

            repo = event.get("repo", {}).get("name", "")
            for item in parser(repo, event.get("payload", {})):
                if item["type"] == "commit":
                    results["commits"].append(item)
                else:
                    results["events"].append(item)

    except urllib.error.URLError as e:
        results["error"] = str(e)

    return results
