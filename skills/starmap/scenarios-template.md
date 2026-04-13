# Scenarios Template

Use this structure when charting a starmap (SCENARIOS-<project>.md).

SCENARIOS is a pure coverage document — it defines what must be true, not how to implement it. No file targets, no code architecture, no execution strategy. Those belong in Stage 2 (Design).

```markdown
# <Project> Scenarios

> Goal: <one-line goal>
> Verification: <how to verify each scenario>
> Reference sources: <external system, docs, source code, specs — list all that apply>

Status: [ ] pending, [x] passing, [~] partial (needs upstream change)
Reserved suffixes: (codex-deferred: ...), (codex-override: ...) — see "Reserved State Suffixes" below

---

## Phase 1: <Foundation>

### 1.1 <Section Name>

- [ ] Scenario A — concrete, testable statement
- [ ] Scenario B — another concrete case
- [ ] Scenario C
...

### 1.2 <Section Name>

- [ ] Scenario D
- [ ] Scenario E
...

## Phase 2: <Next Layer>

### 2.1 <Section Name>
...
```

## Structure Rules

**Phases** are ordered by dependency:
- Phase 1 must pass before Phase 2 makes sense
- Example: basic cases before combinations, single features before interactions

**Sections** within a phase are coverage units:
- Target 5-25 scenarios per section
- Group by feature area or object type
- Execution order (sequential, parallel, or prep-gated) is decided in Stage 2, not here

**Scenarios** are concrete and binary:
- Each is one specific test case (a SQL statement, an API call, a specific input)
- Pass or fail, no "mostly works"
- Named by what they test: `SELECT FROM with alias` not `test alias completion`
- Describes the expected behavior, not the implementation approach

## Reserved State Suffixes

Most scenarios live in one of three states: `[ ]` pending, `[x]` passing, or `[~]` partial with a free-form reason such as `(parser limitation)` or `(upstream issue #123)`. Those free-form partial reasons are human-facing notes — the driver treats them as "blocked, leave alone."

The Stage 3 Codex review loop introduces two additional states that look similar but mean something very different. These **must** use the reserved suffix format below so the driver can distinguish them from human partial notes.

**Reserved words — do not use as free-form partial reasons:**

- `codex-deferred:` — at the start of a partial suffix
- `codex-override:` — at the start of a passing suffix

### `[~] scenario — (codex-deferred: <scope-id>)`

**Meaning**: Driver's Codex review returned `needs-attention` after 2 auto-fix attempts. The scenario's code may contain an issue that Codex flagged; the fix worker tried twice and couldn't satisfy the reviewer. Execution has moved on, but this scenario needs user triage before the starmap is complete.

**Format**: `<scope-id>` is either `batch-<id>` (batch-level defer) or `phase-<id>` (phase-level defer), matching the entry in the driver's `## Deferred Codex Findings` section.

**Driver behavior**:
- `next` and `run-all` **skip** these scenarios — they do not re-dispatch section workers against them
- `status` and `report` count them in a separate "Deferred" bucket, not under normal "Partial"
- Step 12 end-of-run triage reads all `(codex-deferred: ...)` scenarios and presents them for user decision
- A scenario cannot move from `(codex-deferred: ...)` back to plain `[ ]` or `[~]` without going through triage

**Example**:
```
- [~] SELECT DISTINCT with window function — (codex-deferred: batch-3)
```

### `[x] scenario — (codex-override: <justification>)`

**Meaning**: The scenario is marked passing, but with an explicit user-accepted risk: Codex flagged a finding during review, the user deemed it a false positive or acceptable risk during Step 12 triage, and chose to override rather than fix. The override is durable and auditable.

**Format**: `<justification>` is a short verbatim user explanation. The full justification is also recorded in the driver's `## Codex Overrides` section for audit.

**Driver behavior**:
- Counted as passing in the normal `[x]` progress total
- `status` and `report` surface the override count separately from "real" passing, so the distinction stays visible in progress views:
  ```
  Passing:         2,831  [x]
  Override-passed:     8  [x] (codex-override)
  ```
- Anyone reading the SCENARIOS file later can see exactly which scenarios carry accepted risk and why — the suffix is the single source of truth, not a comment that rots

**Example**:
```
- [x] NOT NULL column without DEFAULT on empty table — (codex-override: warning only, intentional for schema linting context)
```

### Why these are reserved

Without this convention, three incompatible meanings collapse into plain `[~]`/`[x]`:

1. `[~] (parser limitation)` — "waiting on upstream, do nothing" (human-facing note)
2. `[~] (codex-deferred: ...)` — "driver defer, triage required" (machine state)
3. `[x] (codex-override: ...)` — "passing with accepted risk" (audit marker)

If a human writes a free-form `[~] (codex integration TBD)` as a comment, the driver's regex would incorrectly treat it as a deferred entry and pull it into Step 12 triage. If a `(codex-override: ...)` annotation is missed, an accepted-risk scenario becomes indistinguishable from a clean pass — an audit hole.

**Rule**: only the driver writes `codex-deferred:` and `codex-override:`. Humans writing partial notes must use other wording (`blocked by upstream`, `parser limitation`, `pending grammar fix`, etc.).

## What Does NOT Belong in SCENARIOS

- File targets (`Targets: diff.go`) — this is an architecture decision, made in Stage 2
- Shared file annotations (`Shared: parser.go`) — this is change-surface analysis, done in Stage 2
- Proof commands (`Proof: go test -run TestX`) — this is test strategy, decided in Stage 2
- Implementation notes ("use a switch statement", "split into per-type files") — Stage 2

If you find yourself writing about files, functions, or code structure in SCENARIOS, stop — you're mixing coverage with design.

## How to Be Thorough

For each feature area, systematically enumerate:

| Dimension | Examples |
|-----------|----------|
| **All variants** | every type, option, flag, mode |
| **Defaults** | what happens when unspecified |
| **Edge cases** | empty, max length, special chars, reserved words |
| **Combinations** | feature A + feature B together |
| **Error cases** | what should fail and with what error |
| **Implicit behavior** | auto-naming, type coercion, default values |

Use all available reference sources as checklists — official docs section by section, grammar rules, source code branches, existing test patterns.

## Sizing Guide

| Project scope | Target scenarios | Typical phases |
|--------------|-----------------|----------------|
| Small (one feature area) | 50-100 | 2-3 |
| Medium (subsystem) | 100-300 | 3-5 |
| Large (full compatibility) | 300-500 | 5-8 |
