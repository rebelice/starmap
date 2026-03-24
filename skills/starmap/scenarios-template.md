# Scenarios Template

Use this structure when charting a starmap (SCENARIOS-<project>.md).

SCENARIOS is a pure coverage document — it defines what must be true, not how to implement it. No file targets, no code architecture, no execution strategy. Those belong in Stage 2 (Design).

```markdown
# <Project> Scenarios

> Goal: <one-line goal>
> Verification: <how to verify each scenario>
> Reference sources: <external system, docs, source code, specs — list all that apply>

Status: [ ] pending, [x] passing, [~] partial (needs upstream change)

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
