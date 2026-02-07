"""Collector de commits en repos git locales."""

import os
import subprocess


def _git_user(repo_path: str) -> str:
    """Obtiene el user.name configurado en el repo."""
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

    results = {"source": "git_local", "repos": []}
    seen_commits = set()

    for repo_path in repos:
        repo_path = os.path.expanduser(repo_path)
        if not os.path.isdir(repo_path):
            continue

        repo_name = os.path.basename(repo_path)
        author = _git_user(repo_path)
        commits = []

        try:
            cmd = [
                "git", "-C", repo_path, "log",
                f"--since={date}T00:00:00",
                f"--until={date}T23:59:59",
                "--format=%h|%s|%an",
                "--all",
            ]
            if author:
                cmd.append(f"--author={author}")

            result = subprocess.run(cmd, capture_output=True, text=True)

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|", 2)
                if len(parts) == 3:
                    sha = parts[0]
                    if sha in seen_commits:
                        continue
                    seen_commits.add(sha)
                    commits.append({
                        "sha": sha,
                        "message": parts[1],
                        "author": parts[2],
                    })

        except Exception as e:
            commits = [{"error": str(e)}]

        if commits:
            results["repos"].append({"name": repo_name, "commits": commits})

    return results
