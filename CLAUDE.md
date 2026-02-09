# Daily Log

CLI tool that collects daily developer activity from multiple sources and generates a Markdown summary using Claude API.

## Structure

```
daily-log                    # Shell wrapper (entry point)
src/
  daily_log.py               # Main: config, summarizer, CLI
  setup.py                   # Interactive setup
  api.py                     # HTTP helpers: fetch(), github(), shortcut(), wakatime()
  ui.py                      # Terminal UI: pastel ANSI colors, unicode symbols
  collectors/
    __init__.py              # Re-exports ALL = [(name, fn), ...]
    github.py                # Commits, PRs, issues, reviews
    shortcut.py              # Stories, epics (filtered by member history)
    git_local.py             # Commits in local repos (filtered by author)
    wakatime.py              # Coding time per project, activity blocks
    claude_code.py           # Chat sessions from ~/.claude/history.jsonl
reports/                     # Generated daily reports (YYYY/MM/YYYY-MM-DD.md)
openspec/                    # Spec-driven development (OpenSpec)
```

## Commands

```bash
daily-log                    # Generate today's report
daily-log --date 2026-02-05  # Specific date
daily-log --dry-run          # Show collected data, no file output
daily-log --no-ai            # Plain markdown, skip Claude API
daily-log --clear            # Delete today's report (to regenerate)
daily-log --setup            # Interactive config setup
```

## Config

Stored at `~/.config/daily-log/config.json`. Env vars override config values:
`GITHUB_TOKEN`, `GITHUB_USERNAME`, `SHORTCUT_TOKEN`, `ANTHROPIC_API_KEY`.

## Architecture

- **Collectors**: Each in `src/collectors/`, registered in `__init__.py`. Returns dict with `source` key and `events` list.
- **Event format**: All collectors return `{"type", "timestamp", "source", "title", "meta"}` dicts.
- **API helpers**: `src/api.py` — `fetch()`, `github()`, `shortcut()`, `wakatime()`.
- **Summarizer**: `generate_summary` calls Claude API; `_fallback_summary` generates markdown without AI.
- **UI**: `src/ui.py` — pastel ANSI 256 colors, unicode symbols, no emojis.
- **Output**: `reports/YYYY/MM/YYYY-MM-DD.md` with raw data in `<details>`.
- **Skip logic**: If data hasn't changed vs existing report, skip regeneration.

## Reports

Reports in `reports/` are the primary output. NEVER delete, overwrite, or discard report files. When committing, always preserve existing reports. If a report appears deleted in git status, restore it.

## Style

- No emojis. Pastel colors and unicode symbols only.
- Python 3.9 compatible (use `Optional`/`Union`, not `X | Y` type hints).
- Stdlib only — no external dependencies.
