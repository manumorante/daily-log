## ADDED Requirements

### Requirement: WakaTime coding_summary event
WakaTime collector SHALL emit `coding_summary` events with `type: "coding_summary"`, `source: "wakatime"`, `title` as "{project} — {human_readable_time}", and `meta` containing `project` (str), `total_seconds` (float), `languages` (dict of language name to seconds), `human_additions` (int), `human_deletions` (int).

#### Scenario: Coding summary event structure
- **WHEN** WakaTime summaries include project "founderz" with 13260 seconds, languages {"PHP": 7800, "Blade": 4920}
- **THEN** the event is `{"type": "coding_summary", "timestamp": "2026-02-06T00:00:00+01:00", "source": "wakatime", "title": "founderz — 3 hrs 41 mins", "meta": {"project": "founderz", "total_seconds": 13260, "languages": {"PHP": 7800, "Blade": 4920}, "human_additions": 120, "human_deletions": 45}}`

### Requirement: WakaTime coding_block event
WakaTime collector SHALL emit `coding_block` events with `type: "coding_block"`, `source: "wakatime"`, `title` as "{project} ({duration}min)", and `meta` containing `project` (str), `duration_seconds` (float), `human_additions` (int), `human_deletions` (int).

#### Scenario: Coding block event structure
- **WHEN** WakaTime durations include a block at Unix time 1770505200.0 for project "daily-log" with duration 482.23 seconds
- **THEN** the event is `{"type": "coding_block", "timestamp": "2026-02-08T00:00:00+01:00", "source": "wakatime", "title": "daily-log (8min)", "meta": {"project": "daily-log", "duration_seconds": 482.23, "human_additions": 39, "human_deletions": 80}}`
