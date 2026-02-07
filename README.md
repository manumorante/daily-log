# Daily Log

CLI tool that collects daily developer activity from multiple sources and generates a Markdown summary using the Claude API.

## Sources

| Source | Collects | Requires |
|--------|----------|----------|
| **GitHub** | Commits, PRs, issues, reviews | `github_token` + `github_username` |
| **Shortcut** | Updated and completed stories | `shortcut_token` |
| **Local git** | Commits in local repos | Paths in `git_repos` |

## Install

```bash
git clone <your-repo> daily-log
cd daily-log
python3 src/setup.py
chmod +x daily-log
```

No external dependencies — stdlib only (Python 3).

## Config

Setup creates `~/.config/daily-log/config.json`:

```json
{
  "github_token": "ghp_...",
  "github_username": "your-user",
  "shortcut_token": "your-token",
  "anthropic_api_key": "sk-ant-...",
  "git_repos": ["~/Code/project-1", "~/Code/project-2"],
  "anthropic_model": "claude-sonnet-4-5-20250514"
}
```

Env vars override config values: `GITHUB_TOKEN`, `GITHUB_USERNAME`, `SHORTCUT_TOKEN`, `ANTHROPIC_API_KEY`.

## Usage

```bash
./daily-log                    # Today's log
./daily-log --date 2026-02-05  # Specific date
./daily-log --dry-run          # Show collected data, no file output
./daily-log --no-ai            # Plain markdown, skip Claude API
./daily-log --output-dir ~/x   # Custom output directory
```

## Output

```
~/daily-logs/YYYY/MM/YYYY-MM-DD.md
```

## Adding sources

Create a `collect_xxx` function in `src/daily_log.py`:

```python
def collect_xxx(config: dict, date: str) -> dict:
    return {"source": "xxx", "data": [...]}
```

Register it in the `collectors` array inside `main()`.
