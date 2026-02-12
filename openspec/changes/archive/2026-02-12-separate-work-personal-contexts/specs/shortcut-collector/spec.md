## ADDED Requirements

### Requirement: Always work context
The collector SHALL add `"context": "work"` to all events. Shortcut is a Founderz-only tool and all stories/epics are work-related.

#### Scenario: Story event is always work
- **WHEN** collecting a story event
- **THEN** the event includes `"context": "work"`

#### Scenario: Epic event is always work
- **WHEN** collecting an epic event
- **THEN** the event includes `"context": "work"`
