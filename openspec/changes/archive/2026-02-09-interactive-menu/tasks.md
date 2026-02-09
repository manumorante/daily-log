## 1. Rewrite ui.py with Rich

- [x] 1.1 Create shared Rich Console instance with built-in color names (no custom Theme)
- [x] 1.2 Rewrite color functions, symbol constants, and output helpers using console.print() with Rich's built-in styles
- [x] 1.3 Add spinner(message) context manager using rich.console.Console.status()
- [x] 1.4 Verify no-color mode works when stdout is not a TTY

## 2. Interactive menu

- [x] 2.1 Create menu function that displays app header and beaupy.select() with options: "Report de hoy", "Report de ayer", "Report de otra fecha", "Borrar report", "Setup", "Salir"
- [x] 2.2 Implement menu loop: execute selected action, return to menu, exit on "Salir"
- [x] 2.3 Handle Ctrl+C (KeyboardInterrupt and beaupy.Abort) for clean exit at any point
- [x] 2.4 Implement "Report de otra fecha" action: beaupy.prompt() for date with today as default
- [x] 2.5 Implement "Borrar report" action: beaupy.prompt() for date, then delete report

## 3. Refactor main() dispatch

- [x] 3.1 Extract report generation logic from main() into a reusable function (generate_report(config, date, no_ai, dry_run))
- [x] 3.2 Extract clear logic into a reusable function (clear_report(config, date))
- [x] 3.3 Refactor main(): if flags passed → direct execution; if no flags + TTY → menu loop; if no flags + non-TTY → generate today
- [x] 3.4 Wire menu actions to extracted functions (report de hoy/ayer/fecha → generate_report, borrar → clear_report, setup → exec setup.py)

## 4. Update collector progress display

- [x] 4.1 Replace print(end="", flush=True) collector progress pattern with Rich spinner or status display
- [x] 4.2 Replace AI summary "Generating..." message with Rich spinner
