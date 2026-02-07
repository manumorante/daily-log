# Daily Log

CLI tool that collects daily developer activity from multiple sources and generates a Markdown summary using Claude API.

## Structure

```
daily-log                    # Shell wrapper (entry point)
src/
  daily_log.py               # Main: config, summarizer, CLI
  setup.py                   # Interactive setup
  api.py                     # HTTP helpers: fetch(), github(), shortcut()
  ui.py                      # Terminal UI: colores pastel ANSI, simbolos
  collectors/
    __init__.py              # Re-exporta ALL = [(name, fn), ...]
    github.py                # Commits, PRs, issues, reviews
    shortcut.py              # Stories actualizadas/completadas
    git_local.py             # Commits en repos locales
openspec/                    # Spec-driven development (OpenSpec)
```

## Commands

```bash
./daily-log                    # Generate today's log
./daily-log --date 2026-02-05  # Specific date
./daily-log --dry-run          # Show collected data, no file output
./daily-log --no-ai            # Plain markdown, skip Claude API
./daily-log --setup            # Interactive config setup
```

## Config

Stored at `~/.config/daily-log/config.json`. Env vars override config values:
`GITHUB_TOKEN`, `GITHUB_USERNAME`, `SHORTCUT_TOKEN`, `ANTHROPIC_API_KEY`.

## Architecture

- **Collectors**: Cada uno en `src/collectors/`, registrado en `__init__.py`. Devuelve dict con clave `source`.
- **API helpers**: `src/api.py` — `fetch()`, `github()`, `shortcut()` eliminan boilerplate HTTP.
- **Summarizer**: `generate_summary` llama a Claude API; `_fallback_summary` genera markdown sin AI.
- **UI**: `src/ui.py` — colores pastel ANSI (256), simbolos unicode (●○▲✕▸), sin emojis.
- **Output**: `~/daily-logs/YYYY/MM/YYYY-MM-DD.md` con datos crudos en `<details>`.
- **Skip logic**: Si los datos no cambiaron respecto al log existente, no regenera.

## Style

- Sin emojis. UI con colores pastel y simbolos unicode.
- Python 3.9 compatible (no usar `X | Y` en type hints, usar `Optional`/`Union`).
- Sin dependencias externas — stdlib only.

## Dependencies

None — stdlib only (urllib, json, subprocess, argparse).
