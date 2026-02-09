## 1. Dependency

- [x] 1.1 Install beaupy (`pip install beaupy`)

## 2. Rewrite setup.py

- [x] 2.1 Define declarative SECTIONS list (name, check, fields with key/label/secret)
- [x] 2.2 Write `setup_section(config, section)` that prompts fields using beaupy `prompt`/`prompt(secure=True)`
- [x] 2.3 Write `setup_repos(config)` as custom handler: `confirm` for auto-scan, `prompt` for dirs, `select_multiple` for repo selection (all pre-ticked)
- [x] 2.4 Rewrite reconfigure flow: `confirm` to reconfigure, `select_multiple` for section selection
- [x] 2.5 Rewrite `main()` using SECTIONS + `setup_section` + custom handlers
- [x] 2.6 Translate all Spanish strings to English

## 3. Verification

- [x] 3.1 Run `./daily-log --setup` and walk through full setup flow
- [x] 3.2 Run `./daily-log --setup` with everything already configured (reconfigure path)
