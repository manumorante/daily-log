# Daily Log

CLI tool that collects daily developer activity from multiple sources and generates a Markdown summary using the Claude API.

## Sources

| Source | Collects | Requires |
|--------|----------|----------|
| **GitHub** | Commits, PRs, issues, reviews | `github_token` + `github_username` |
| **Shortcut** | Updated and completed stories, epics | `shortcut_token` |
| **Local git** | Commits in local repos | Paths in `git_repos` |
| **WakaTime** | Coding time per project and language | `wakatime_api_key` |
| **Claude Code** | Chat sessions grouped by project | None (reads `~/.claude/history.jsonl`) |

## Install

```bash
git clone <your-repo> daily-log
cd daily-log
./daily-log --setup
```

No external dependencies — stdlib only (Python 3.9+).

## Config

Setup creates `~/.config/daily-log/config.json`:

```json
{
  "github_token": "ghp_...",
  "github_username": "your-user",
  "shortcut_token": "your-token",
  "anthropic_api_key": "sk-ant-...",
  "wakatime_api_key": "waka_...",
  "git_repos": ["~/projects/project-1", "~/projects/project-2"],
  "anthropic_model": "claude-sonnet-4-5-20250929"
}
```

Env vars override config values: `GITHUB_TOKEN`, `GITHUB_USERNAME`, `SHORTCUT_TOKEN`, `ANTHROPIC_API_KEY`.

Optional: `claude_history_path` defaults to `~/.claude/history.jsonl`.

## Usage

```bash
daily-log                    # Today's report
daily-log --date 2026-02-05  # Specific date
daily-log --dry-run          # Show collected data, no file output
daily-log --no-ai            # Plain markdown, skip Claude API
daily-log --clear            # Delete today's report (to regenerate)
daily-log --setup            # Interactive config setup
```

## Output

```
reports/YYYY/MM/YYYY-MM-DD.md
```

## Adding sources

Create a collector in `src/collectors/`:

```python
# src/collectors/xxx.py
def collect_xxx(config: dict, date: str) -> dict:
    events = [{"type": "xxx", "timestamp": "...", "source": "xxx", "title": "...", "meta": {}}]
    return {"source": "xxx", "events": events}
```

Register it in `src/collectors/__init__.py`:

```python
from .xxx import collect_xxx

ALL = [
    ...
    ("Xxx", collect_xxx),
]
```
