# Scenarios Template

Use this structure when charting a starmap (SCENARIOS.md).

```markdown
# <Project> Scenarios

> Goal: <one-line goal>
> Verification: <how to verify each scenario>
> Oracle: <reference system or spec>

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

## Phase 3: <Advanced>
...
```

## Structure Rules

**Phases** are ordered by dependency:
- Phase 1 must pass before Phase 2 makes sense
- Example: output formatting before error messages, basic types before combinations

**Sections** within a phase are independent:
- Can be executed in any order
- Each section is one worker invocation
- Target 5-25 scenarios per section

**Scenarios** are concrete and binary:
- Each is one specific test case (a SQL statement, an API call, a specific input)
- Pass or fail, no "mostly works"
- Named by what they test: `INT UNSIGNED` not `test unsigned integer type`

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

Use the reference system's official documentation as a checklist. Read it section by section and extract every distinct behavior into a scenario.

## Sizing Guide

| Project scope | Target scenarios | Typical phases |
|--------------|-----------------|----------------|
| Small (one feature area) | 50-100 | 2-3 |
| Medium (subsystem) | 100-300 | 3-5 |
| Large (full compatibility) | 300-500 | 5-8 |
