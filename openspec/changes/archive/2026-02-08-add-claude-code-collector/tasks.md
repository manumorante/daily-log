## 1. Collector implementation

- [x] 1.1 Create `src/collectors/claude_code.py` with `collect_claude_code(config, date)` function
- [x] 1.2 Implement history file reading: open `claude_history_path` (default `~/.claude/history.jsonl`), parse each line as JSON, filter by date
- [x] 1.3 Implement session grouping: group entries by `(sessionId, project)`, compute start/end timestamps, message count
- [x] 1.4 Implement title extraction: skip `/commands`, `exit`, `pwd`, messages < 5 chars; use first meaningful message truncated to 80 chars; fallback to "Claude Code session"
- [x] 1.5 Implement project path simplification: strip home dir + `projects/` prefix

## 2. Registration

- [x] 2.1 Add import and register `("Claude Code", collect_claude_code)` in `src/collectors/__init__.py`
- [x] 2.2 Add `claude_history_path` default to config in `src/daily_log.py` (only if config loading needs it)

## 3. Verification

- [x] 3.1 Run `./daily-log --dry-run` and verify Claude Code sessions appear in output
- [x] 3.2 Run `./daily-log --no-ai` and verify sessions render in the markdown report
- [x] 3.3 Test with `--date` for a day with known Claude Code activity
