# setup-wizard Specification

## Purpose
TBD - created by archiving change bootstrap-specs. Update Purpose after archive.
## Requirements
### Requirement: Interactive configuration
`setup.py` SHALL provide an interactive CLI that prompts for all data source credentials and saves to `~/.config/daily-log/config.json`.

#### Scenario: First-time setup
- **WHEN** `daily-log --setup` is run with no existing config
- **THEN** all sections are prompted in order: GitHub, Shortcut, Claude API, WakaTime, Git repos

#### Scenario: Partial config exists
- **WHEN** some sources are already configured
- **THEN** configured sources show a check mark and only unconfigured sources are prompted

### Requirement: Setup sections
The wizard SHALL have 5 sections: GitHub (token + username), Shortcut (token), Claude API (key + model), WakaTime (key), Git repos (auto-scan or manual paths). Secret values SHALL use `getpass` for hidden input.

#### Scenario: Secret input
- **WHEN** the user is prompted for a token
- **THEN** input is hidden (not echoed to terminal)

### Requirement: Git repo auto-discovery
The wizard SHALL offer to auto-scan directories for git repos using `find` with configurable base directories and max depth of 2. Found repos are listed and the user can select all or specific ones.

#### Scenario: Auto-scan finds 5 repos
- **WHEN** the user chooses to auto-scan and 5 repos are found
- **THEN** all 5 are listed with numbers and the user can choose all or select specific ones by number

### Requirement: Reconfiguration
When all sections are already configured, the wizard SHALL offer to reconfigure. The user can select specific sections by number.

#### Scenario: All configured, user reconfigures one
- **WHEN** all sections are configured and user chooses to reconfigure section 1
- **THEN** only the GitHub section is re-prompted

