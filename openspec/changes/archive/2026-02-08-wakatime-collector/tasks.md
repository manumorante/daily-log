## 1. API Helper

- [x] 1.1 Add `wakatime(path, api_key)` function to `src/api.py` with Basic auth (base64 of `key:`)

## 2. Collector

- [x] 2.1 Create `src/collectors/wakatime.py` with `collect_wakatime(config, date)` function
- [x] 2.2 Fetch `/users/current/summaries` and emit `coding_summary` events (one per project)
- [x] 2.3 Fetch `/users/current/durations` and emit `coding_block` events (one per block, convert Unix timestamp to ISO 8601)
- [x] 2.4 Handle empty responses gracefully (old dates, no activity)
- [x] 2.5 Register collector in `src/collectors/__init__.py`

## 3. Config and Setup

- [x] 3.1 Add `wakatime_api_key` to `DEFAULT_CONFIG` in `src/daily_log.py`
- [x] 3.2 Add `WAKATIME_API_KEY` env var override in `load_config()`
- [x] 3.3 Add WakaTime API key prompt to `src/setup.py`
