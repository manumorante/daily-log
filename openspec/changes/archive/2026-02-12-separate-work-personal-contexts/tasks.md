## 1. Context Constants Module

- [x] 1.1 Create `src/context.py` module
- [x] 1.2 Define `WORK_GITHUB_USERNAME = "manumorante-fdz"`
- [x] 1.3 Define `WORK_PATH_PATTERNS = ["founderz/"]`
- [x] 1.4 Define `WORK_PROJECT_KEYWORDS = ["founderz"]`
- [x] 1.5 Define `WORK_ONLY_SOURCES = ["shortcut"]`

## 2. Update GitHub Collector

- [x] 2.1 Import `WORK_GITHUB_USERNAME` from `src.context`
- [x] 2.2 Add context detection logic: check if username matches `WORK_GITHUB_USERNAME`
- [x] 2.3 Add `"context": "work"` or `"context": "personal"` to each event based on username
- [x] 2.4 Verify all event types (commit, pr, issue, review) include context field

## 3. Update Git Local Collector

- [x] 3.1 Import `WORK_PATH_PATTERNS` from `src.context`
- [x] 3.2 Add context detection logic: check if any pattern appears in repo path
- [x] 3.3 Add `"context": "work"` or `"context": "personal"` to each event based on path
- [x] 3.4 Verify context is correctly detected for multiple repos with mixed contexts

## 4. Update WakaTime Collector

- [x] 4.1 Import `WORK_PROJECT_KEYWORDS` from `src.context`
- [x] 4.2 Add context detection logic: check if any keyword appears in project name (case-insensitive)
- [x] 4.3 Add `"context": "work"` or `"context": "personal"` to coding_summary events
- [x] 4.4 Add `"context": "work"` or `"context": "personal"` to coding_block events
- [x] 4.5 Verify case-insensitive matching works correctly

## 5. Update Shortcut Collector

- [x] 5.1 Add `"context": "work"` to all story events
- [x] 5.2 Add `"context": "work"` to all epic events

## 6. Disable Claude Code Collector

- [x] 6.1 Comment out `from .claude_code import collect_claude_code` in `src/collectors/__init__.py`
- [x] 6.2 Comment out `("Claude Code", collect_claude_code)` in the `ALL` list with reason comment

## 7. Update Report Output

- [x] 7.1 Modify `write_report()` to accept `context` parameter
- [x] 7.2 Update report path generation to use `{reports_dir}/{context}/YYYY/MM/YYYY-MM-DD.md` format
- [x] 7.3 Add context filtering logic to only include events matching the context
- [x] 7.4 Ensure directory structure is created automatically for both work and personal subdirs
- [x] 7.5 Handle empty context reports with "No {context} activity recorded" message

## 8. Update Main Flow (daily_log.py)

- [x] 8.1 Update event collection to aggregate all events from collectors
- [x] 8.2 Add context filtering logic: separate events into work_events and personal_events
- [x] 8.3 Update report generation to call `write_report()` for selected context(s)
- [x] 8.4 Handle default behavior (work only) when no context specified
- [x] 8.5 Add support for generating both contexts when requested
- [x] 8.6 Add default to "personal" with warning for events missing context field

## 9. Update Interactive Menu

- [x] 9.1 Add context selection prompt using `beaupy.select()` with options: "work" (default), "personal", "both"
- [x] 9.2 Update "Today's report" flow to prompt for context before generating
- [x] 9.3 Update "Yesterday's report" flow to prompt for context before generating
- [x] 9.4 Update "Report for a date" flow to prompt for context after date entry
- [x] 9.5 Update "Delete report" flow to prompt for context before deletion
- [x] 9.6 Update deletion logic to handle both single context and "both" selections
- [x] 9.7 Update deletion messages for non-existent context reports

## 10. Testing

- [x] 10.1 Test GitHub collector context detection with both accounts
- [x] 10.2 Test Git local collector context detection with founderz and personal repos
- [x] 10.3 Test WakaTime collector context detection with mixed projects
- [x] 10.4 Test Shortcut collector always adds work context
- [x] 10.5 Test work report generation contains only work events
- [x] 10.6 Test personal report generation contains only personal events
- [x] 10.7 Test "both" generates two separate report files
- [x] 10.8 Test default behavior generates only work report
- [x] 10.9 Test interactive menu context selection flow
- [x] 10.10 Test report deletion for each context option
- [x] 10.11 Test empty context reports show "No activity recorded" message
- [x] 10.12 Verify old reports remain untouched in original location
