"""Collector for local git repo commits."""

import os
import subprocess


def _git_user(repo_path: str) -> str:
    """Get the user.name configured in the repo."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "config", "user.name"],
            capture_output=True, text=True,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def collect_git_local(config: dict, date: str) -> dict:
    repos = config.get("git_repos", [])
    if not repos:
        return {"source": "git_local", "status": "skipped", "reason": "no repos configured"}

    events = []
    seen = set()

    for repo_path in repos:
        repo_path = os.path.expanduser(repo_path)
        if not os.path.isdir(repo_path):
            continue

        repo_name = os.path.basename(repo_path)
        author = _git_user(repo_path)

        try:
            cmd = [
                "git", "-C", repo_path, "log",
                f"--since={date}T00:00:00",
                f"--until={date}T23:59:59",
                "--format=%h|%s|%an|%aI",
                "--all",
            ]
            if author:
                cmd.append(f"--author={author}")

            result = subprocess.run(cmd, capture_output=True, text=True)

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|", 3)
                if len(parts) == 4:
                    sha = parts[0]
                    if sha in seen:
                        continue
                    seen.add(sha)
                    events.append({
                        "type": "commit",
                        "timestamp": parts[3],
                        "source": "git_local",
                        "title": parts[1],
                        "meta": {
                            "sha": sha,
                            "repo": repo_name,
                            "author": parts[2],
                        },
                    })

        except Exception:
            pass

    return {"source": "git_local", "events": events}
