## Why

The setup wizard uses plain `input()` calls — typing "s/n" for confirmations and comma-separated numbers for repo selection. Replacing these with beaupy's interactive prompts (arrow-key select, checkboxes, confirm) gives a premium first-run experience with minimal code changes.

## What Changes

- Add `beaupy` as first external dependency (pip install)
- Rewrite `src/setup.py` prompts to use beaupy's `select`, `select_multiple`, `confirm`, and `prompt`
- Same flow, same sections, same config output — just better navigation
- Translate remaining Spanish strings in setup.py to English

## Capabilities

### New Capabilities
- `interactive-setup`: Setup wizard using beaupy for arrow-key navigation, checkboxes, and styled prompts

### Modified Capabilities

None. Config format and collector behavior remain identical.

## Impact

- New dependency: `beaupy` (pip install)
- Modified: `src/setup.py` (rewritten prompts)
- No changes to collectors, config format, or CLI flags
