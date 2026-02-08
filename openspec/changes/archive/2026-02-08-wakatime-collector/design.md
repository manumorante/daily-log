## Context

daily-log has three collectors (github, shortcut, git_local) that follow a common pattern: receive `(config, date)`, call an API, return `{"source": "...", "events": [...]}`. The `api.py` module provides helper functions (`github()`, `shortcut()`) that wrap `fetch()` with service-specific auth headers. WakaTime has a REST API at `api.wakatime.com/api/v1` with Basic auth (base64-encoded API key). Two endpoints are relevant: `/summaries` (aggregated time per project/language) and `/durations` (individual activity blocks). Both work on the free plan but data is only available for the last 7 days.

## Goals / Non-Goals

**Goals:**
- Add a WakaTime collector that emits events following the existing event format
- Provide both aggregated time (per project) and granular activity blocks
- Handle free-plan limitations gracefully (7-day retention)
- Follow the same patterns as existing collectors (same signature, same registration)

**Non-Goals:**
- Time estimation or session calculation (future change: `time-estimation-foundation`)
- Task linking via branch names (future change)
- Persisting WakaTime data beyond what the report captures
- Supporting WakaTime OAuth flow (API key is sufficient)

## Decisions

### API helper pattern
Add `wakatime(path, api_key)` to `api.py` following the same pattern as `github()` and `shortcut()`. WakaTime uses HTTP Basic auth where the API key is the username with an empty password: `Authorization: Basic base64(key + ":")`.

**Alternative**: Pass the API key as query param (`?api_key=XXX`). Rejected because it exposes the key in logs and is less consistent with the existing header-based pattern.

### Two event types from one collector
The collector makes two API calls (summaries + durations) and emits two distinct event types:
- `coding_summary`: One per project. Total seconds, language breakdown. For the daily report.
- `coding_block`: One per activity block. Start time, duration, project. For future timeline/session analysis.

**Alternative**: Only emit summaries (simpler). Rejected because duration blocks are essential for future time-per-task work and the data is only available for 7 days — if we don't capture it now, it's lost.

### Timestamp handling
WakaTime durations use Unix timestamps (seconds since epoch). Convert to ISO 8601 with the timezone from the API response to match the event format convention. Summaries don't have per-entry timestamps; use the date's start-of-day as timestamp.

### Graceful degradation for old dates
If the API returns empty data (date outside 7-day window), return the standard `{"source": "wakatime", "events": []}` — no error, just no events. The collector should not fail or warn loudly since this is expected behavior for `--date` with old dates.

## Risks / Trade-offs

- [Free plan retention] WakaTime free only keeps 7 days of data → Mitigation: daily-log captures the data in the report file, so it's preserved permanently. Document the limitation.
- [Rate limiting] WakaTime allows ~10 req/s average over 5min → Mitigation: we only make 2 requests per run, well within limits.
- [Project name mismatch] WakaTime project names may differ from git repo names (e.g., "manumorante" vs "dotfiles") → Mitigation: accept as-is for now; project name mapping is a future concern for task-linking.
- [No branch info] Free plan durations don't include branch names in the response → Mitigation: project name still provides grouping signal; branch linking will come from enriching git_local collector separately.
