"""Collector for GitHub activity."""

import urllib.error
from api import github


def _parse_push(repo, payload, ts):
    return [
        {
            "type": "commit",
            "timestamp": ts,
            "source": "github",
            "title": c.get("message", "").split("\n")[0],
            "meta": {"sha": c.get("sha", "")[:7], "repo": repo},
        }
        for c in payload.get("commits", [])
    ]


def _parse_pr(repo, payload, ts):
    return [{
        "type": "pr",
        "timestamp": ts,
        "source": "github",
        "title": payload.get("pull_request", {}).get("title", ""),
        "meta": {
            "action": payload.get("action", ""),
            "repo": repo,
            "number": payload.get("pull_request", {}).get("number"),
        },
    }]


def _parse_issue(repo, payload, ts):
    return [{
        "type": "issue",
        "timestamp": ts,
        "source": "github",
        "title": payload.get("issue", {}).get("title", ""),
        "meta": {"action": payload.get("action", ""), "repo": repo},
    }]


def _parse_review(repo, payload, ts):
    return [{
        "type": "review",
        "timestamp": ts,
        "source": "github",
        "title": payload.get("pull_request", {}).get("title", ""),
        "meta": {"repo": repo},
    }]


_PARSERS = {
    "PushEvent": _parse_push,
    "PullRequestEvent": _parse_pr,
    "IssuesEvent": _parse_issue,
    "PullRequestReviewEvent": _parse_review,
}


def collect_github(config: dict, date: str) -> dict:
    token, username = config.get("github_token"), config.get("github_username")
    if not token or not username:
        return {"source": "github", "status": "skipped", "reason": "no token/username"}

    events = []

    try:
        raw_events = github(f"users/{username}/events?per_page=100", token)

        for event in raw_events:
            ts = event.get("created_at", "")
            if ts[:10] != date:
                continue

            parser = _PARSERS.get(event["type"])
            if not parser:
                continue

            repo = event.get("repo", {}).get("name", "")
            events.extend(parser(repo, event.get("payload", {}), ts))

    except urllib.error.URLError as e:
        return {"source": "github", "events": [], "error": str(e)}

    return {"source": "github", "events": events}
