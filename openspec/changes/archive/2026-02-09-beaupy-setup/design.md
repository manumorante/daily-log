## Context

`src/setup.py` is the interactive config wizard. It has 5 sections (GitHub, Shortcut, Claude API, WakaTime, Git repos), each using `input()` for text and "s/n" strings for yes/no. Repo selection uses comma-separated numbers. The flow detects what's already configured, only prompts for missing sections, and allows reconfiguration of existing ones.

## Goals / Non-Goals

**Goals:**
- Replace `input()` prompts with beaupy equivalents: `prompt`, `confirm`, `select`, `select_multiple`
- Keep the exact same setup flow and config output
- Translate all Spanish UI strings to English

**Non-Goals:**
- Changing the config format or adding new config keys
- Adding validation beyond what exists today
- Full TUI app with textual/curses — this stays a sequential wizard

## Decisions

### Use beaupy directly, no fallback
The project has decided to accept beaupy as a dependency. No `try/except ImportError` fallback to raw input — keep the code simple. If beaupy is not installed, setup fails with a clear import error.

**Alternative**: Conditional import with fallback. Rejected — adds complexity for a scenario we don't need. The user installs the tool, they install the dependency.

### Prompt-by-prompt replacement
Each existing `input()`/`ask()` call maps to a beaupy function:

| Current | beaupy |
|---------|--------|
| `ask("text", default)` | `beaupy.prompt("text", initial_value=default)` |
| `ask("text", secret=True)` | `beaupy.prompt("text", secure=True)` |
| `ask("s/n", "s")` | `beaupy.confirm("question")` |
| Number selection from list | `beaupy.select(options)` |
| Comma-separated multi-select | `beaupy.select_multiple(options)` |

### Declarative section definitions
Replace individual `setup_xxx()` functions with a data-driven approach. Each section is a dict describing its fields:

```python
SECTIONS = [
    {"name": "GitHub", "check": lambda c: c.get("github_token") and c.get("github_username"),
     "fields": [
        {"key": "github_username", "label": "Username"},
        {"key": "github_token", "label": "Token (ghp_...)", "secret": True},
    ]},
    ...
]
```

A single `setup_section(config, section)` function handles prompting for all standard sections. Special sections (like Git repos with scan + multi-select) use a `"custom": fn` key that overrides the default behavior.

This makes adding a new collector's setup a one-liner: add a dict to SECTIONS.

### Keep existing ui.py for non-interactive output
Headers, separators, status indicators (OK/SKIP) stay with `ui.py`. beaupy handles only the interactive prompts.

## Risks / Trade-offs

- **[New dependency]** → beaupy is small (~50KB), pure Python, actively maintained. Acceptable trade-off for UX.
- **[Terminal compatibility]** → beaupy uses ANSI escape codes. Works on all modern terminals. Same assumption we already make with ui.py colors.
