## ADDED Requirements

### Requirement: Read Claude Code history file
The collector SHALL read `~/.claude/history.jsonl` (or the path in config key `claude_history_path`). Each line is a JSON object with keys: `display`, `timestamp`, `project`, `sessionId`.

#### Scenario: Default path exists
- **WHEN** no `claude_history_path` is configured
- **THEN** the collector reads `~/.claude/history.jsonl`

#### Scenario: Custom path configured
- **WHEN** config contains `claude_history_path` set to `/other/path/history.jsonl`
- **THEN** the collector reads `/other/path/history.jsonl`

#### Scenario: File does not exist
- **WHEN** the history file is not found
- **THEN** the collector returns `{"source": "claude_code", "status": "skipped", "reason": "history file not found"}`

### Requirement: Filter entries by date
The collector SHALL only process entries whose `timestamp` (millisecond epoch) falls within the requested date in local timezone.

#### Scenario: Entry matches requested date
- **WHEN** an entry has timestamp `1769511096320` and the requested date is `2026-01-27`
- **THEN** the entry is included in processing

#### Scenario: Entry from different date
- **WHEN** an entry has a timestamp from `2026-01-28` and the requested date is `2026-01-27`
- **THEN** the entry is excluded

### Requirement: Group messages into sessions
The collector SHALL group filtered entries by the combination of `sessionId` and `project`. Each unique pair produces one `claude_session` event.

#### Scenario: Same session, same project
- **WHEN** 5 entries share `sessionId: "abc"` and `project: "/Users/me/projects/foo"`
- **THEN** they produce 1 event with `message_count: 5`

#### Scenario: Same session, different projects
- **WHEN** 3 entries have `sessionId: "abc"` with `project: "foo"` and 2 have `sessionId: "abc"` with `project: "bar"`
- **THEN** they produce 2 separate events

### Requirement: Session event title from first meaningful message
The title SHALL be the `display` field of the first message in the group that is not a command (`/`-prefixed), `exit`, `pwd`, or shorter than 5 characters. The title SHALL be truncated to 80 characters.

#### Scenario: First message is meaningful
- **WHEN** a session's first message is "he pensado en usar la IA para organizar bookmarks de chrome para un usuario"
- **THEN** the event title is `"he pensado en usar la IA para organizar bookmarks de chrome para un usuario"`

#### Scenario: First messages are commands
- **WHEN** a session's messages are `["/init", "exit", "guiame para probar el proyecto"]`
- **THEN** the event title is `"guiame para probar el proyecto"`

#### Scenario: All messages are commands
- **WHEN** a session only contains `["/init", "exit"]`
- **THEN** the event title is `"Claude Code session"`

#### Scenario: Long first message
- **WHEN** the first meaningful message is 120 characters long
- **THEN** the title is truncated to 80 characters

### Requirement: Simplify project paths
The collector SHALL strip the home directory and `projects/` prefix from project paths, showing clean relative names.

#### Scenario: Standard project path
- **WHEN** project is `/Users/manumorante/projects/personal/ia/daily-log`
- **THEN** meta.project is `personal/ia/daily-log`

#### Scenario: Non-standard path
- **WHEN** project is `/Users/manumorante/some-other-place`
- **THEN** meta.project is `some-other-place`

### Requirement: Session timestamps
Each event SHALL use the earliest entry timestamp as `timestamp` and include `end_time` in meta with the latest entry timestamp. Both SHALL be ISO 8601 in local timezone.

#### Scenario: Session spanning 2 hours
- **WHEN** a session has entries from 10:00 to 12:00
- **THEN** `timestamp` is `2026-02-07T10:00:00+01:00` and `meta.end_time` is `2026-02-07T12:00:00+01:00`

### Requirement: Collector signature
The function SHALL be `collect_claude_code(config: dict, date: str) -> dict` and return `{"source": "claude_code", "events": [...]}` following the standard collector format.

#### Scenario: Normal collection
- **WHEN** 3 sessions are found for the date
- **THEN** returns `{"source": "claude_code", "events": [<3 events>]}`

#### Scenario: No sessions for date
- **WHEN** no entries match the requested date
- **THEN** returns `{"source": "claude_code", "events": []}`
