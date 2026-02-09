# config-system Specification

## Purpose
TBD - created by archiving change bootstrap-specs. Update Purpose after archive.
## Requirements
### Requirement: Config file location
Configuration SHALL be stored at `~/.config/daily-log/config.json`. The directory SHALL be created automatically if it does not exist.

#### Scenario: First run
- **WHEN** `load_config()` is called and no config file exists
- **THEN** it creates `~/.config/daily-log/config.json` with default values and exits with a message to run `--setup`

### Requirement: Default config keys
`DEFAULT_CONFIG` SHALL include: `github_token`, `github_username`, `shortcut_token`, `anthropic_api_key`, `wakatime_api_key`, `git_repos` (list), `anthropic_model`.

#### Scenario: Default config created
- **WHEN** config is created for the first time
- **THEN** all keys are present with empty strings or empty lists as defaults

### Requirement: Environment variable overrides
The following env vars SHALL override config values: `GITHUB_TOKEN` → `github_token`, `GITHUB_USERNAME` → `github_username`, `SHORTCUT_TOKEN` → `shortcut_token`, `ANTHROPIC_API_KEY` → `anthropic_api_key`, `WAKATIME_API_KEY` → `wakatime_api_key`.

#### Scenario: Env var set
- **WHEN** `GITHUB_TOKEN` is set in environment
- **THEN** it overrides `github_token` from config file

#### Scenario: Env var not set
- **WHEN** `GITHUB_TOKEN` is not in environment
- **THEN** the value from config file is used

### Requirement: Reports directory override
The config SHALL support an optional `reports_dir` key to override the default reports location (`~/daily-log/reports`). Resolution order: `--output-dir` CLI flag > `reports_dir` in config > default.

#### Scenario: Custom reports_dir in config
- **WHEN** `reports_dir` is set to `~/my-logs` in config
- **THEN** reports are written to `~/my-logs/YYYY/MM/YYYY-MM-DD.md`

