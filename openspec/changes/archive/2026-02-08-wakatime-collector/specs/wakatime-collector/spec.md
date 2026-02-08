## ADDED Requirements

### Requirement: WakaTime API helper
`api.py` SHALL provide a `wakatime(path, api_key)` function that calls `https://api.wakatime.com/api/v1/{path}` with HTTP Basic auth (API key as username, empty password).

#### Scenario: Successful API call
- **WHEN** `wakatime("users/current/summaries?start=2026-02-08&end=2026-02-08", key)` is called
- **THEN** it returns the parsed JSON response from the WakaTime API

#### Scenario: Invalid API key
- **WHEN** `wakatime()` is called with an invalid key
- **THEN** it raises `urllib.error.HTTPError` with status 401

### Requirement: Collector signature and registration
`collect_wakatime(config, date)` SHALL follow the same signature as other collectors. It SHALL be registered in `src/collectors/__init__.py` in the `ALL` list.

#### Scenario: Collector registered
- **WHEN** daily-log imports collectors
- **THEN** `ALL` includes `("wakatime", collect_wakatime)`

#### Scenario: No API key configured
- **WHEN** `wakatime_api_key` is missing from config
- **THEN** it returns `{"source": "wakatime", "status": "skipped", "reason": "no api key"}`

### Requirement: Fetch coding summaries
The collector SHALL call `/users/current/summaries?start={date}&end={date}` and emit one `coding_summary` event per project with `total_seconds`, `languages` breakdown, and `human_additions`/`human_deletions` counts.

#### Scenario: Day with activity in two projects
- **WHEN** WakaTime returns summaries with projects "founderz" (3h41min) and "dotfiles" (52min)
- **THEN** the collector emits two `coding_summary` events, one per project, each with `meta.total_seconds`, `meta.languages`, and `meta.human_additions`/`meta.human_deletions`

#### Scenario: Day with no activity
- **WHEN** WakaTime returns summaries with an empty projects list
- **THEN** the collector returns `{"source": "wakatime", "events": []}`

### Requirement: Fetch duration blocks
The collector SHALL call `/users/current/durations?date={date}` and emit one `coding_block` event per activity block with the start timestamp (converted from Unix to ISO 8601), duration in seconds, and project name.

#### Scenario: Day with multiple blocks
- **WHEN** WakaTime returns 5 duration blocks
- **THEN** the collector emits 5 `coding_block` events, each with `meta.duration_seconds` and `meta.project`

#### Scenario: Unix timestamp conversion
- **WHEN** a duration block has `time: 1770505200.0` and the API response has `timezone: "Europe/Madrid"`
- **THEN** the event timestamp SHALL be converted to ISO 8601 in that timezone

### Requirement: Graceful handling of old dates
When the API returns empty data for dates outside the free-plan retention window, the collector SHALL return an empty events list without errors.

#### Scenario: Date outside retention window
- **WHEN** `collect_wakatime` is called with a date 30 days ago
- **THEN** it returns `{"source": "wakatime", "events": []}` (no error, no warning)

### Requirement: Config and setup
`wakatime_api_key` SHALL be added to `DEFAULT_CONFIG`. The env var `WAKATIME_API_KEY` SHALL override the config value. `setup.py` SHALL prompt for the WakaTime API key during interactive setup.

#### Scenario: Env var override
- **WHEN** `WAKATIME_API_KEY` is set in environment
- **THEN** it overrides the value from `config.json`

#### Scenario: Setup prompts for key
- **WHEN** user runs `daily-log --setup`
- **THEN** setup asks for WakaTime API key (optional, can be left blank)
