## 1. Collectors with timestamps

- [x] 1.1 git_local: change format to `%h|%s|%an|%aI` and include timestamp in each commit
- [x] 1.2 github: include `created_at` from the events API in each event
- [x] 1.3 shortcut: capture `changed_at` from history when filtering by member

## 2. Unified event format

- [x] 2.1 Define helper function to create events: `_event(type, timestamp, source, title, meta)`
- [x] 2.2 Adapt git_local to return `{"source": "git_local", "events": [...]}`
- [x] 2.3 Adapt github to return `{"source": "github", "events": [...]}`
- [x] 2.4 Adapt shortcut to return `{"source": "shortcut", "events": [...]}`

## 3. JSON summarizer

- [x] 3.1 Change SUMMARY_PROMPT to request JSON with schema (highlight, code, tasks, patterns, risks)
- [x] 3.2 Parse Claude response as JSON with fallback to plain text
- [x] 3.3 Adapt `_fallback_summary` to generate the same JSON schema from events

## 4. Render from JSON

- [x] 4.1 Create `_render_markdown(date, summary_json)` function to generate .md from JSON
- [x] 4.2 Show only `highlight` in terminal after generation
- [x] 4.3 Adapt main() to use the new flow: events → JSON → render

## 5. Verification

- [x] 5.1 Test with --dry-run: verify unified event format
- [x] 5.2 Test with --no-ai: verify fallback generates valid JSON and correct render
- [x] 5.3 Full test: verify Claude JSON and .md render
