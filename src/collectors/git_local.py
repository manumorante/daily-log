"""Collector for local git repo commits."""

import os
import subprocess

from collectors._utils import extract_task_id


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


def _parse_branch_from_refs(refs_str):
    """Pick the best branch name from a comma-separated %D ref string."""
    if not refs_str:
        return ""
    for ref in refs_str.split(","):
        ref = ref.strip()
        if not ref:
            continue
        if ref.startswith("HEAD -> "):
            ref = ref[len("HEAD -> "):]
        if ref.startswith("origin/") or ref.startswith("tag: "):
            continue
        return ref
    return ""


def _build_branch_map(repo_path):
    """Build sha→branch map by parsing git log --all --format=%h|%D."""
    branch_map = {}
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "log", "--all", "--format=%h|%D"],
            capture_output=True, text=True,
        )
        for line in result.stdout.strip().split("\n"):
            if not line or "|" not in line:
                continue
            sha, refs = line.split("|", 1)
            sha = sha.strip()
            branch = _parse_branch_from_refs(refs.strip())
            if sha and branch and sha not in branch_map:
                branch_map[sha] = branch
    except Exception:
        pass
    return branch_map


def _branch_contains_fallback(repo_path, sha):
    """Fallback: use git branch --contains to find branch for a commit."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "branch", "--contains", sha],
            capture_output=True, text=True,
        )
        for line in result.stdout.strip().split("\n"):
            name = line.strip().lstrip("* ")
            if name and name not in ("main", "master"):
                return name
        # All branches are main/master — return the first one
        for line in result.stdout.strip().split("\n"):
            name = line.strip().lstrip("* ")
            if name:
                return name
    except Exception:
        pass
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
        branch_map = _build_branch_map(repo_path)

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
                    branch = branch_map.get(sha, "")
                    if not branch:
                        branch = _branch_contains_fallback(repo_path, sha)

                    meta = {
                        "sha": sha,
                        "repo": repo_name,
                        "author": parts[2],
                    }
                    if branch:
                        meta["branch"] = branch
                        tid = extract_task_id(branch)
                        if tid:
                            meta["task_id"] = tid

                    events.append({
                        "type": "commit",
                        "timestamp": parts[3],
                        "source": "git_local",
                        "title": parts[1],
                        "meta": meta,
                    })

        except Exception:
            pass

    return {"source": "git_local", "events": events}
