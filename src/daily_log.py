#!/usr/bin/env python3
"""
Daily Log Generator
Collects daily developer activity from multiple sources and generates a summary with Claude.
"""

import os
import sys
import json
import urllib.error
from datetime import datetime
from pathlib import Path

# Local imports
sys.path.insert(0, str(Path(__file__).parent))
import ui
from api import fetch
from collectors import ALL as COLLECTORS

# ─── Config ──────────────────────────────────────────────────────────────────

APP_NAME = "daily-log"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"
LOGS_DIR = Path.home() / APP_NAME / "reports"

DEFAULT_CONFIG = {
    "github_token": "",
    "github_username": "",
    "shortcut_token": "",
    "anthropic_api_key": "",
    "wakatime_api_key": "",
    "git_repos": [],
    "anthropic_model": "claude-sonnet-4-5-20250929",
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
        ui.warn(f"Config created at: {CONFIG_FILE}")
        ui.info("Run: daily-log --setup")
        sys.exit(1)

    config = json.loads(CONFIG_FILE.read_text())

    env_map = {
        "GITHUB_TOKEN": "github_token",
        "GITHUB_USERNAME": "github_username",
        "SHORTCUT_TOKEN": "shortcut_token",
        "ANTHROPIC_API_KEY": "anthropic_api_key",
        "WAKATIME_API_KEY": "wakatime_api_key",
    }
    for env_key, config_key in env_map.items():
        val = os.environ.get(env_key)
        if val:
            config[config_key] = val

    return config


# ─── Summarizer ──────────────────────────────────────────────────────────────

SUMMARY_PROMPT = """You are an assistant that analyzes daily developer activity.

You will receive a JSON array of events from different sources (GitHub, Shortcut, local git).
Each event has: type, timestamp, source, title, meta.

Respond with ONLY a valid JSON object (no markdown, no explanation) with this exact schema:

{{
  "highlight": "2-3 sentence summary of the most important activity of the day. Write in Spanish.",
  "code": [
    {{"group": "group name", "items": ["commit description 1", "commit description 2"]}}
  ],
  "tasks": [
    {{"id": 123, "name": "task name", "status": "in_progress|completed", "note": "optional observation"}}
  ],
  "patterns": ["observation about work patterns, sessions, or trends"],
  "risks": ["risk or concern identified from the data"]
}}

Rules:
- Write all text content in Spanish
- Group related commits together in "code" (don't list merge commits individually)
- "tasks" comes from Shortcut story events
- "patterns" should note temporal patterns (e.g., intense sessions, long-running tasks)
- "risks" should flag concerns (e.g., stories stuck too long, no reviews)
- Empty sections must be empty arrays [], never omit keys
- Respond with ONLY the JSON object, nothing else

Events for {date}:
"""


def _collect_events(collected: list) -> list:
    """Extract all events from collected data into a flat list."""
    events = []
    for source in collected:
        events.extend(source.get("events", []))
    return events


def generate_summary(config: dict, date: str, events: list) -> dict:
    api_key = config.get("anthropic_api_key")
    if not api_key:
        return _fallback_summary(events)

    model = config.get("anthropic_model", "claude-sonnet-4-5-20250929")
    prompt = (
        SUMMARY_PROMPT.replace("{date}", date)
        + json.dumps(events, indent=2, ensure_ascii=False)
    )

    try:
        result = fetch(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": model,
                "max_tokens": 2048,
                "messages": [{"role": "user", "content": prompt}],
            }).encode("utf-8"),
        )
        text = "\n".join(
            b["text"] for b in result.get("content", []) if b.get("type") == "text"
        ).strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1]  # remove first line (```json)
            text = text.rsplit("```", 1)[0]  # remove closing ```
        return json.loads(text.strip())

    except (json.JSONDecodeError, KeyError):
        ui.err("Claude returned invalid JSON, using fallback")
        return _fallback_summary(events)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(body).get("error", {}).get("message", body)
        except Exception:
            detail = body
        ui.err(f"Claude API: {e.code} {e.reason}")
        ui.info(detail)
        return _fallback_summary(events)
    except Exception as e:
        ui.err(f"Claude API: {e}")
        return _fallback_summary(events)


def _fallback_summary(events: list) -> dict:
    """Generate the same JSON schema from raw events without AI."""
    code_by_repo = {}
    tasks = []

    for ev in events:
        t = ev.get("type", "")
        meta = ev.get("meta", {})

        if t == "commit":
            repo = meta.get("repo", "unknown")
            code_by_repo.setdefault(repo, []).append(ev.get("title", ""))
        elif t in ("pr", "issue", "review"):
            repo = meta.get("repo", "unknown")
            code_by_repo.setdefault(repo, []).append(
                f"{t.upper()}: {ev.get('title', '')}"
            )
        elif t == "story":
            status = "completed" if meta.get("completed") else "in_progress"
            tasks.append({
                "id": meta.get("id"),
                "name": ev.get("title", ""),
                "status": status,
                "note": meta.get("workflow_state", ""),
            })
        elif t == "epic":
            tasks.append({
                "id": meta.get("id"),
                "name": ev.get("title", ""),
                "status": meta.get("state", ""),
                "note": "epic",
            })

    code = [{"group": repo, "items": items} for repo, items in code_by_repo.items()]

    return {
        "highlight": "",
        "code": code,
        "tasks": tasks,
        "patterns": [],
        "risks": [],
    }


def _render_markdown(date: str, summary: dict) -> str:
    """Render a summary JSON dict into a markdown report."""
    lines = [f"## Daily report — {date}\n"]

    highlight = summary.get("highlight", "")
    if highlight:
        lines.append(highlight)
        lines.append("")

    patterns = summary.get("patterns", [])
    risks = summary.get("risks", [])
    if patterns or risks:
        for p in patterns:
            lines.append(f"- {p}")
        for r in risks:
            lines.append(f"- **Risk:** {r}")
        lines.append("")

    tasks = summary.get("tasks", [])
    if tasks:
        done = [t for t in tasks if t.get("status") == "completed"]
        active = [t for t in tasks if t.get("status") != "completed"]
        if done:
            lines.append("### Completed\n")
            for t in done:
                note = f" — {t['note']}" if t.get("note") else ""
                lines.append(f"- {t.get('name', '')} (#{t.get('id', '')}){note}")
            lines.append("")
        if active:
            lines.append("### In progress\n")
            for t in active:
                note = f" — {t['note']}" if t.get("note") else ""
                lines.append(f"- {t.get('name', '')} (#{t.get('id', '')}){note}")
            lines.append("")

    code = summary.get("code", [])
    if code:
        lines.append("### Code\n")
        for group in code:
            lines.append(f"**{group['group']}**")
            for item in group.get("items", []):
                lines.append(f"- {item}")
            lines.append("")

    return "\n".join(lines)


def _has_changes(log_file: Path, raw: str) -> bool:
    """Compare current raw data with the existing log."""
    try:
        content = log_file.read_text()
        start = content.find("```json\n")
        end = content.find("\n```\n\n</details>")
        if start == -1 or end == -1:
            return True
        existing_raw = content[start + 8:end]
        return existing_raw.strip() != raw.strip()
    except Exception:
        return True


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="daily-log",
        description="Collect daily developer activity from GitHub, Shortcut and local git, and generate a summary with Claude.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  daily-log                    Generate today's report\n"
               "  daily-log --date 2026-02-05  Report for a specific date\n"
               "  daily-log --dry-run          Show collected data only\n"
               "  daily-log --clear            Delete today's report\n"
               "  daily-log --no-ai            Report without Claude summary\n"
               "  daily-log --setup            Configure tokens and repos",
    )
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="report date (default: today)")
    parser.add_argument("--no-ai", action="store_true",
                        help="generate report without Claude summary")
    parser.add_argument("--dry-run", action="store_true",
                        help="show collected events without generating report")
    parser.add_argument("--clear", action="store_true",
                        help="delete the report for the given date")
    parser.add_argument("--setup", action="store_true",
                        help="configure tokens and repos")
    parser.add_argument("--output-dir", default=None,
                        help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.setup:
        setup_script = Path(__file__).parent / "setup.py"
        os.execvp(sys.executable, [sys.executable, str(setup_script)])

    config = load_config()
    date = args.date
    output_dir = Path(args.output_dir or config.get("reports_dir") or LOGS_DIR)

    if args.clear:
        year_month = date[:7].replace("-", "/")
        log_file = output_dir / year_month / f"{date}.md"
        short_path = str(log_file).replace(str(Path.home()), "~")
        if log_file.exists():
            log_file.unlink()
            ui.done(f"Deleted: {short_path}")
        else:
            ui.info(f"No report for {date}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    ui.header(f"daily-log {ui.dim(date)}")

    # Check configured sources
    missing = []
    if not config.get("github_token") or not config.get("github_username"):
        missing.append("GitHub (token / username)")
    if not config.get("shortcut_token"):
        missing.append("Shortcut (token)")
    if not config.get("git_repos"):
        missing.append("Git local repos")

    if len(missing) == 3:
        ui.warn("No data sources configured:")
        for m in missing:
            ui.item(ui.dim(m))
        print()
        ui.info("Run: daily-log --setup")
        print()
        sys.exit(1)

    if missing:
        ui.warn("Unconfigured sources (will be skipped):")
        for m in missing:
            ui.item(ui.dim(m))
        ui.info("Complete with: daily-log --setup")
        print()

    # Collect data
    collected = []
    for name, collector in COLLECTORS:
        print(f"  {ui.dim('▸')} {name}", end="  ", flush=True)
        try:
            data = collector(config, date)
            status = data.get("status", "ok")
            if status == "skipped":
                print(ui.dim(f"○ {data.get('reason', '')}"))
            elif "error" in data:
                print(f"{ui.WARN} {ui.yellow(data['error'])}")
            else:
                print(ui.OK)
            collected.append(data)
        except Exception as e:
            print(f"{ui.ERR} {ui.red(str(e))}")
            collected.append({"source": name.lower(), "error": str(e)})

    # Flatten events
    events = _collect_events(collected)

    if args.dry_run:
        print()
        ui.info("Collected events:")
        print(json.dumps(events, indent=2, ensure_ascii=False))
        return

    # Report path
    year_month = date[:7].replace("-", "/")
    log_dir = output_dir / year_month
    log_file = log_dir / f"{date}.md"
    short_path = str(log_file).replace(str(Path.home()), "~")

    raw = json.dumps(events, indent=2, ensure_ascii=False)

    if log_file.exists() and not _has_changes(log_file, raw):
        ui.info(f"No new changes: {short_path}")
        return

    # Generate summary
    ui.separator()
    if args.no_ai:
        summary = _fallback_summary(events)
    else:
        ui.run("Generating summary with Claude...")
        summary = generate_summary(config, date, events)

    # Render and save
    log_dir.mkdir(parents=True, exist_ok=True)
    markdown = _render_markdown(date, summary)
    output = (
        markdown
        + "\n---\n\n"
        + "<details>\n<summary>Raw data</summary>\n\n"
        + f"```json\n{raw}\n```\n\n"
        + "</details>\n"
    )
    log_file.write_text(output)

    # Show highlight in terminal
    highlight = summary.get("highlight", "")
    if highlight:
        print(f"  {highlight}")
    print()
    ui.done(short_path)


if __name__ == "__main__":
    main()
