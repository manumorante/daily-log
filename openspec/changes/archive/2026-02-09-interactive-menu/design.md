## Context

daily-log is a CLI tool that collects developer activity and generates markdown reports. Currently it runs in a single-shot mode: parse flags, execute, exit. The UI layer is split between raw ANSI helpers (`ui.py`) and beaupy/Rich (only in `setup.py`). Rich is already installed as a transitive dependency of beaupy.

The user wants a menu-driven experience where `daily-log` (no args) presents an interactive menu, and all actions are accessible via arrow keys + Enter.

## Goals / Non-Goals

**Goals:**
- Single interactive entry point that replaces flag memorization
- Unified UI rendering through Rich (output) + beaupy (input)
- Menu loop: action completes → return to menu
- Backward-compatible: flags still work for scripting/cron

**Non-Goals:**
- Full TUI framework (Textual, curses) — this is a simple select-based menu
- Changing report format or collector logic
- Rewriting setup.py — it already uses beaupy correctly
- Adding new features beyond the menu (no new collectors, no new report sections)

## Decisions

### 1. Rich Console as the single output engine

**Decision**: Rewrite `ui.py` internals to use `rich.console.Console`. Keep the same public API (`ok()`, `err()`, `header()`, `warn()`, etc.).

**Rationale**: Rich is already installed (beaupy dependency). Using it directly gives consistent rendering with beaupy's interactive widgets. Raw ANSI escapes are fragile across terminal emulators.

**Alternative considered**: Keep raw ANSI. Rejected because it creates two visual systems (ANSI for output, Rich for input) and limits future capabilities (no spinners, no tables).

### 2. beaupy.select() for the main menu

**Decision**: Use `beaupy.select()` for the main menu and any single-choice prompts. Use `beaupy.confirm()` for yes/no. Use `beaupy.prompt()` for text input (date entry).

**Rationale**: beaupy is already a dependency and provides exactly the keyboard-driven selection needed. No new dependencies.

**Alternative considered**: Rich's built-in `Prompt`. Rejected because it requires typing, not arrow-key selection.

### 3. Menu loop in main()

**Decision**: Refactor `main()` in `daily_log.py`:
- If any CLI flag is passed → direct execution (current behavior, no menu)
- If no flags → enter menu loop: show menu → execute action → repeat until "Exit"

**Rationale**: Preserves backward compatibility. Scripts and cron jobs that use `daily-log --date X` keep working.

### 4. Use Rich's built-in styles

**Decision**: Use Rich's standard color names (`green`, `yellow`, `red`, `blue`, `cyan`, `dim`) directly. No custom Theme, no ANSI 256 codes.

**Rationale**: Less code, zero configuration. Rich's defaults look good. The custom pastel palette was a workaround for raw ANSI — with Rich there's no need to maintain a palette.

### 5. Spinner for long operations

**Decision**: Use `rich.console.Console.status()` for spinners during collector execution and AI summary generation.

**Rationale**: Built into Rich, no extra dependency. Replaces the current `print(end="", flush=True)` + `print(OK)` pattern with a proper spinner.

## Risks / Trade-offs

- **[Visual differences]** Colors will change from custom pastel ANSI 256 to Rich defaults → Accepted by user: prefer simplicity over custom palette.
- **[TTY detection]** Menu requires a TTY. Piping output or running in non-interactive mode must fall back → Mitigation: detect `sys.stdout.isatty()` and skip menu if not TTY (use direct mode).
- **[beaupy exceptions]** beaupy raises `Abort` on Ctrl+C → Mitigation: catch `beaupy.Abort` and `KeyboardInterrupt` in menu loop for clean exit.
