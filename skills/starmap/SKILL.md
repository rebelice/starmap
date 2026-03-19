---
name: starmap
description: Use when a project requires matching the complete behavior of a reference
  system, achieving full feature coverage against a specification, or systematically
  migrating between systems
---

# Starmap

Chart a complete map of every scenario between where you are and where you need to be, then navigate there one section at a time.

## When to Use

**Use starmap when:**
- Compatibility: "make X behave identically to Y"
- Coverage: "support all features of Z"
- Migration: "migrate from A to B completely"
- Any goal where progress = "how many concrete scenarios pass against a reference"

**Don't use when:**
- No reference system to verify against — use writing-plans instead
- Fewer than 50 scenarios — use subagent-driven-development instead

Starmap complements Superpowers: use writing-plans for goals without an oracle, subagent-driven-development for smaller scoped goals.

## The Process

```
/starmap init      → Interactive: define goal, generate SCENARIOS.md + worker + driver skills
```

### Step 1: Define the Goal

Present these questions to the user one at a time. If an answer is vague, ask follow-up questions to make it concrete. If the user cannot identify an oracle, suggest alternatives or redirect to writing-plans.

1. **What is the goal?** (e.g., "MySQL catalog matches MySQL 8.0 behavior")
2. **What is the verification surface?** (e.g., "SHOW CREATE TABLE output exact match")
3. **What is the oracle/reference?** (e.g., "real MySQL 8.0 via testcontainers")
4. **Where does the project live?** (e.g., `mysql/catalog/`)

### Step 2: Chart the Starmap

Decompose into scenarios following ./scenarios-template.md. Structure: phases (ordered by dependency) > sections (independent within phase, 5-25 scenarios each) > scenarios (concrete, binary pass/fail).

### Step 3: Generate Skills

Generate a **worker** skill (./worker-template.md) and a **driver** skill (./driver-template.md), customized for the project's test patterns, verification commands, and commit conventions.

### Step 4: Review

Dispatch a fresh review subagent using ./reviewer-prompt.md before execution begins.

### Step 5: Execute

Use the generated driver skill: `status`, `plan`, `next`, `run X.Y`, `run-all`, `report`.

## Key Principles

1. **SCENARIOS.md is the source of truth** — checkboxes ARE the progress
2. **Oracle is authoritative** — never adjust expectations to match implementation
3. **One section at a time** — focused unit of work with its own commit
4. **Progress is monotonic** — once a scenario passes, it never regresses

## Anti-Patterns

- **Scenarios too vague**: "handle all numeric types" — each type should be separate
- **Worker doing too much**: if 20+ scenarios fail, fix 5-10, commit, let driver re-dispatch the rest
- **Skipping the oracle**: unit tests without oracle comparison give false confidence
- **Not updating SCENARIOS.md**: progress is invisible if checkboxes aren't updated
