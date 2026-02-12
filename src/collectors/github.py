"""Collector for GitHub activity."""

import urllib.error
from api import github
from collectors._utils import branch_meta
from context import WORK_GITHUB_USERNAME


def _parse_push(repo, payload, ts, username):
    ref = payload.get("ref", "")
    branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else ""
    enrichment = branch_meta(branch)
    context = "work" if username == WORK_GITHUB_USERNAME else "personal"
    return [
        {
            "type": "commit",
            "timestamp": ts,
            "source": "github",
            "context": context,
            "title": c.get("message", "").split("\n")[0],
            "meta": {"sha": c.get("sha", "")[:7], "repo": repo, **enrichment},
        }
        for c in payload.get("commits", [])
    ]


def _parse_pr(repo, payload, ts, username):
    branch = payload.get("pull_request", {}).get("head", {}).get("ref", "")
    enrichment = branch_meta(branch)
    context = "work" if username == WORK_GITHUB_USERNAME else "personal"
    return [{
        "type": "pr",
        "timestamp": ts,
        "source": "github",
        "context": context,
        "title": payload.get("pull_request", {}).get("title", ""),
        "meta": {
            "action": payload.get("action", ""),
            "repo": repo,
            "number": payload.get("pull_request", {}).get("number"),
            **enrichment,
        },
    }]


def _parse_issue(repo, payload, ts, username):
    context = "work" if username == WORK_GITHUB_USERNAME else "personal"
    return [{
        "type": "issue",
        "timestamp": ts,
        "source": "github",
        "context": context,
        "title": payload.get("issue", {}).get("title", ""),
        "meta": {"action": payload.get("action", ""), "repo": repo},
    }]


def _parse_review(repo, payload, ts, username):
    context = "work" if username == WORK_GITHUB_USERNAME else "personal"
    return [{
        "type": "review",
        "timestamp": ts,
        "source": "github",
        "context": context,
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
            actor_username = event.get("actor", {}).get("login", username)
            events.extend(parser(repo, event.get("payload", {}), ts, actor_username))

    except urllib.error.URLError as e:
        return {"source": "github", "events": [], "error": str(e)}

    return {"source": "github", "events": events}
