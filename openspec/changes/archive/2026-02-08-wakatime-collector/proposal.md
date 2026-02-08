## Why

Current collectors capture discrete actions (commits, PRs, story moves) but miss the actual time spent coding. WakaTime tracks editor activity with second-level precision, giving real coding duration per project and time blocks throughout the day. This is the most reliable signal for estimating daily work hours and will be the foundation for time-per-task calculation.

## What Changes

- Add `wakatime()` helper to `src/api.py` for WakaTime API calls (Basic auth with API key)
- Add `src/collectors/wakatime.py` collector that fetches daily summaries and duration blocks
- Emit `coding_summary` events (one per project, with total time) and `coding_block` events (one per activity block, with start time and duration)
- Register the collector in `src/collectors/__init__.py`
- Add `wakatime_api_key` to config and setup flow
- Handle gracefully when date is outside WakaTime's free-plan retention window (7 days)

## Capabilities

### New Capabilities
- `wakatime-collector`: Fetches daily coding activity from WakaTime API. Emits `coding_summary` events (aggregated time per project) and `coding_block` events (individual activity blocks with timestamps and durations).

### Modified Capabilities
- `event-format`: Add WakaTime event types (`coding_summary`, `coding_block`) to the event schema with their specific meta fields.

## Impact

- `src/api.py`: Add `wakatime()` helper function
- `src/collectors/wakatime.py`: New file
- `src/collectors/__init__.py`: Register new collector
- `src/setup.py`: Add WakaTime API key prompt
- `src/daily_log.py`: Add `wakatime_api_key` to `DEFAULT_CONFIG` and env var override
