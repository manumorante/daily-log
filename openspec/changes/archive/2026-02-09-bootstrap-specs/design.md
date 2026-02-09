## Context

daily-log has 13 distinct capabilities. Only 4 have OpenSpec specs (added post-adoption). The remaining 9 exist only as code. This creates asymmetry: new features get spec-driven development, legacy features don't.

## Goals / Non-Goals

**Goals:**
- Every capability in the system has a spec file in `openspec/specs/`
- Specs are lightweight: responsibility, contract, key behaviors
- Future changes to any area can reference existing specs

**Non-Goals:**
- Exhaustive specification (that happens on-demand when a change touches the area)
- Code changes of any kind
- Modifying existing specs

## Decisions

**Spec granularity: one spec per independently-changeable capability**

Each spec maps to a module or cohesive unit that someone would modify independently. Groupings:
- `report-output` combines rendering + skip logic (both about the report file)
- `cli` covers argparse + orchestration (always change together)
- Collectors get one spec each (changed independently)

Alternative considered: finer granularity (separate skip-logic spec, separate report-render spec). Rejected — too fragmented for the bootstrap pass. Can split later if needed.

**Spec depth: minimal but contractual**

Each spec includes: purpose, input/output, key behaviors, edge cases. Enough for the agent to know what exists and what it should preserve. Not a full requirements doc.

Alternative considered: full detailed specs upfront. Rejected — high effort, specs would go stale. Better to enrich on-demand.

**Delta specs in change, sync to main on archive**

Standard OpenSpec flow. Each new spec is written as a delta spec in the change directory, then synced to `openspec/specs/` on archive.

## Risks / Trade-offs

- [Specs describe current code, not original intent] → Acceptable for bootstrap. Future changes enrich specs with real requirements.
- [9 specs at once is a large batch] → All are lightweight and independent. Can be created in parallel.
