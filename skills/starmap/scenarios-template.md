# Scenarios Template

Use this structure when charting a starmap (SCENARIOS-<project>.md).

```markdown
# <Project> Scenarios

> Goal: <one-line goal>
> Verification: <how to verify each scenario>
> Reference sources: <external system, docs, source code, specs — list all that apply>
> Proof: <section-local proof command> | <batch integration proof command> | <global proof command>

Status: [ ] pending, [x] passing, [~] partial (needs upstream change)

---

## Phase 1: <Foundation>

### 1.1 <Section Name>

> Targets: <files this section will modify>
> Shared: <files shared with other sections in this phase, or "none">
> Proof: <section-specific verification command, or "standard">

- [ ] Scenario A — concrete, testable statement
- [ ] Scenario B — another concrete case
- [ ] Scenario C
...

### 1.2 <Section Name>

> Targets: <files>
> Shared: <files or "none">
> Proof: <command or "standard">

- [ ] Scenario D
- [ ] Scenario E
...

## Phase 2: <Next Layer>

### 2.1 <Section Name>

> Targets: <files>
> Shared: <files or "none">
> Proof: <command or "standard">

...
```

## Structure Rules

**Phases** are ordered by dependency:
- Phase 1 must pass before Phase 2 makes sense
- Example: basic cases before combinations, single features before interactions

**Sections** within a phase are independent:
- Can be executed in any order
- Each section is one worker invocation
- Target 5-25 scenarios per section

**Scenarios** are concrete and binary:
- Each is one specific test case (a SQL statement, an API call, a specific input)
- Pass or fail, no "mostly works"
- Named by what they test: `SELECT FROM with alias` not `test alias completion`

## Change-Surface Annotations

Each section has three annotation fields:

- **Targets**: files this section will create or modify. Best guess at chart time, refined during execution design. Examples: `lib/formatter/primitives.go, lib/formatter/primitives_test.go`
- **Shared**: files that also appear in another section's Targets within the same phase. "none" when fully isolated. This is the key signal for parallelization decisions.
- **Proof**: the verification command that proves this section's work. "standard" means use the project's default test command. Can be narrower (a specific test file) or broader (requires integration test).

These annotations force the question "what does this section actually touch?" even when the answer is simple. A section with `Shared: none` is a one-line annotation, not a burden. But skipping the question entirely is how parallel execution breaks.

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
