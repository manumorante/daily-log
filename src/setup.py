#!/usr/bin/env python3
"""Interactive setup wizard for daily-log."""

import json
import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ui
from beaupy import prompt, confirm, select_multiple


# ─── Config ──────────────────────────────────────────────────────────────────

CONFIG_DIR = Path.home() / ".config" / "daily-log"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "github_token": "",
    "github_username": "",
    "shortcut_token": "",
    "anthropic_api_key": "",
    "wakatime_api_key": "",
    "git_repos": [],
    "anthropic_model": "claude-sonnet-4-5-20250929",
}


# ─── Section definitions ─────────────────────────────────────────────────────

def _check_github(c):
    return bool(c.get("github_token") and c.get("github_username"))


def _check_key(key):
    return lambda c: bool(c.get(key))


def _check_repos(c):
    return bool(c.get("git_repos"))


SECTIONS = [
    {
        "name": "GitHub",
        "check": _check_github,
        "fields": [
            {"key": "github_username", "label": "Username"},
            {"key": "github_token", "label": "Token (ghp_...)", "secret": True},
        ],
    },
    {
        "name": "Shortcut",
        "check": _check_key("shortcut_token"),
        "fields": [
            {"key": "shortcut_token", "label": "API token", "secret": True},
        ],
    },
    {
        "name": "Claude API",
        "check": _check_key("anthropic_api_key"),
        "fields": [
            {"key": "anthropic_api_key", "label": "API key (sk-ant-...)", "secret": True},
            {"key": "anthropic_model", "label": "Model"},
        ],
    },
    {
        "name": "WakaTime",
        "check": _check_key("wakatime_api_key"),
        "fields": [
            {"key": "wakatime_api_key", "label": "API key", "secret": True},
        ],
    },
    {
        "name": "Git repos",
        "check": _check_repos,
        "custom": "setup_repos",
    },
]


# ─── Helpers ─────────────────────────────────────────────────────────────────

def find_git_repos(base_dirs, max_depth=2):
    """Find git repos in the given directories."""
    repos = []
    for base in base_dirs:
        base = os.path.expanduser(base)
        if not os.path.isdir(base):
            continue
        try:
            result = subprocess.run(
                ["find", base, "-maxdepth", str(max_depth), "-name", ".git", "-type", "d"],
                capture_output=True, text=True, timeout=10,
            )
            for line in result.stdout.strip().split("\n"):
                if line:
                    repos.append(os.path.dirname(line))
        except Exception:
            pass
    return sorted(repos)


def setup_section(config, section):
    """Prompt fields for a standard section."""
    print(f"  {ui.dim(section['name'])}")
    for field in section["fields"]:
        current = config.get(field["key"], "")
        value = prompt(
            f"  {field['label']}",
            initial_value=current,
            secure=field.get("secret", False),
        )
        if value:
            config[field["key"]] = value
    print()


def setup_repos(config):
    """Custom handler for git repo selection."""
    print(f"  {ui.dim('Git repos')}")
    if confirm("  Scan for repos automatically?", default_is_yes=True):
        dirs_input = prompt("  Directories to scan (comma-separated)", initial_value="~/projects")
        dirs = [d.strip() for d in dirs_input.split(",")]
        repos = find_git_repos(dirs)
        if repos:
            print(f"\n  Found {len(repos)} repos:\n")
            selected = select_multiple(
                repos,
                ticked_indices=list(range(len(repos))),
                pagination=len(repos) > 10,
                page_size=10,
            )
            config["git_repos"] = selected
        else:
            ui.skip("No repos found.")
    else:
        manual = prompt("  Repo paths (comma-separated)", initial_value="")
        if manual:
            config["git_repos"] = [p.strip() for p in manual.split(",")]
    print()


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    ui.header("daily-log setup")

    # Load existing config or start fresh
    existing = {}
    if CONFIG_FILE.exists():
        existing = json.loads(CONFIG_FILE.read_text())

    config = {**DEFAULT_CONFIG, **existing}

    # Show current status
    pending = []
    configured = []
    for section in SECTIONS:
        if section["check"](config):
            configured.append(section)
        else:
            pending.append(section)

    if configured:
        for s in configured:
            print(f"  {ui.OK} {s['name']}")

    if pending:
        for s in pending:
            print(f"  {ui.SKIP} {ui.dim(s['name'])}")
        print()

        # Only configure what's missing
        for section in pending:
            if "custom" in section:
                setup_repos(config)
            else:
                setup_section(config, section)
    else:
        print()
        if not confirm("  All configured. Reconfigure?", default_is_yes=False):
            print()
            ui.info("Run: ./daily-log")
            return
        print()
        names = [s["name"] for s in SECTIONS]
        selected = select_multiple(names, minimal_count=1)
        print()
        for section in SECTIONS:
            if section["name"] in selected:
                if "custom" in section:
                    setup_repos(config)
                else:
                    setup_section(config, section)

    # Save
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    ui.separator()
    for section in SECTIONS:
        if section["check"](config):
            print(f"  {ui.OK} {section['name']}")
        else:
            print(f"  {ui.SKIP} {ui.dim(section['name'])}")

    ui.done(f"Config saved: {CONFIG_FILE}")
    print()
    ui.info("Run: ./daily-log")


if __name__ == "__main__":
    main()
