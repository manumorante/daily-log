# shortcut-collector Specification

## Purpose
TBD - created by archiving change bootstrap-specs. Update Purpose after archive.
## Requirements
### Requirement: Collector signature and registration
`collect_shortcut(config, date)` SHALL follow the standard collector signature. It SHALL be registered in `src/collectors/__init__.py` in the `ALL` list as `("Shortcut", collect_shortcut)`.

#### Scenario: No token configured
- **WHEN** `shortcut_token` is missing from config
- **THEN** it returns `{"source": "shortcut", "status": "skipped", "reason": "no token"}`

#### Scenario: API error
- **WHEN** the Shortcut API returns an error
- **THEN** it returns `{"source": "shortcut", "events": [], "error": "<message>"}`

### Requirement: Member ID resolution
The collector SHALL use `shortcut_member_id` from config if available. Otherwise it SHALL auto-detect by calling `GET /member` and extracting the `id` field.

#### Scenario: Member ID in config
- **WHEN** `shortcut_member_id` is set in config
- **THEN** it uses that value without calling the API

#### Scenario: Auto-detect member ID
- **WHEN** `shortcut_member_id` is not set
- **THEN** it calls `GET /member` and uses the returned `id`

### Requirement: Collect stories updated on date
The collector SHALL search stories with `updated:{date}` query. When a member ID is available, it SHALL filter stories by checking `/stories/{id}/history` for entries matching the member and date. Each story becomes a `story` event with meta: id, story_type, workflow_state, completed.

#### Scenario: Story completed today by this member
- **WHEN** a story was completed today and the member has history entries for today
- **THEN** a `story` event is emitted with `meta.completed: true` and `meta.workflow_state` resolved from workflow states

#### Scenario: Story updated by another member
- **WHEN** a story was updated today but has no history entries for this member
- **THEN** the story is excluded from results

### Requirement: Collect epics updated on date
The collector SHALL search epics with `updated:{date}` query. Each epic becomes an `epic` event with meta: id, state. Epics are NOT filtered by member.

#### Scenario: Epic updated today
- **WHEN** an epic was updated today
- **THEN** an `epic` event is emitted with `meta.state` from the API response

