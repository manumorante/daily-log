## MODIFIED Requirements

### Requirement: Collect stories updated on date
The collector SHALL search stories with `updated:{date}` query. When a member ID is available, it SHALL filter stories by checking `/stories/{id}/history` for entries matching the member and date. Each story becomes a `story` event with meta: id, task_id, story_type, workflow_state, completed. The `task_id` field SHALL be set to the string representation of the story ID.

#### Scenario: Story completed today by this member
- **WHEN** a story with id 2983 was completed today and the member has history entries for today
- **THEN** a `story` event is emitted with `meta.id: 2983`, `meta.task_id: "2983"`, `meta.completed: true`, and `meta.workflow_state` resolved from workflow states

#### Scenario: Story updated by another member
- **WHEN** a story was updated today but has no history entries for this member
- **THEN** the story is excluded from results
