## Why

The CLI currently requires memorizing flags (`--date`, `--clear`, `--dry-run`, `--no-ai`, `--setup`) and typing exact dates. Running `daily-log` with no arguments immediately executes report generation with no chance to choose what to do. A menu-driven interface lets the user control everything with arrow keys and Enter — no flags to remember, no dates to type.

Additionally, the UI layer is split: `ui.py` uses raw ANSI escapes while `setup.py` uses beaupy (which uses Rich underneath). Unifying on Rich + beaupy gives one consistent visual system across the entire app.

## What Changes

- **New interactive main menu**: Running `daily-log` with no arguments launches an interactive menu instead of immediately generating a report. Menu options replace all current flags.
- **Unified UI layer**: Rewrite `ui.py` to use Rich for output, keeping the same public API (`ok()`, `err()`, `header()`, etc.). beaupy continues handling interactive input (select, prompt, confirm). Both share Rich's rendering engine.
- **Date picker via menu**: "Report for specific date" uses an interactive prompt instead of requiring `--date YYYY-MM-DD`.
- **Menu loop**: After each action completes, the user returns to the main menu. Exit is an explicit menu option.
- **CLI flags still work**: Passing any flag (e.g. `--date`, `--setup`) bypasses the menu and runs directly, preserving scriptability and backward compatibility.

## Capabilities

### New Capabilities
- `interactive-menu`: Main menu loop with keyboard navigation (select action, execute, return). Replaces flag-based dispatch as default entry point.

### Modified Capabilities
- `terminal-ui`: Rewrite internals from raw ANSI to Rich console. Same public API, new rendering engine. Add spinner support.
- `cli`: Default behavior changes from "generate today's report" to "show interactive menu". Flags still work for direct execution.

## Impact

- **`src/ui.py`**: Full rewrite internally (Rich-based), same public function signatures plus new helpers (spinner, menu).
- **`src/daily_log.py`**: `main()` refactored — menu dispatch replaces argparse-only flow. Argparse kept for flag-based direct mode.
- **`src/setup.py`**: No changes needed (already uses beaupy).
- **Dependencies**: Rich is already installed (beaupy dependency). No new deps.
- **`daily-log` shell wrapper**: No changes needed.
- **Reports**: No format changes. Same output.
