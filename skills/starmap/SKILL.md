---
name: starmap
description: Use when a project requires systematic coverage of a large feature area,
  matching the behavior of a reference system, or comprehensively testing a complex
  subsystem
---

# Starmap

Chart a complete map of every scenario between where you are and where you need to be, then navigate there one section at a time.

## When to Use

**Use starmap when:**
- Compatibility: "make X behave identically to Y"
- Coverage: "comprehensively test all aspects of Z"
- Migration: "migrate from A to B completely"
- Any goal where progress = "how many concrete scenarios pass"

**Don't use when:**
- Fewer than 50 scenarios — use subagent-driven-development instead
- No systematic enumeration needed — use writing-plans instead

## The Process

```
/starmap init      → Interactive: define goal, generate SCENARIOS.md + worker + driver skills
```

### Step 1: Define the Goal

Present these questions to the user one at a time:

1. **What is the goal?** (e.g., "comprehensive completion tests for PG parser")
2. **What is the verification surface?** (e.g., "completion results for each SQL context")
3. **Where do expectations come from?** — an external system to run against, official docs/specs, source code analysis, or a combination. All are valid reference sources.
4. **Where does the project live?** (e.g., `backend/plugin/parser/pg/`)

### Step 2: Explore

Dispatch exploration subagents to build a thorough understanding of the territory:

1. **Read source code** — understand what the system does and what it should support
2. **Read documentation** — official specs, grammar definitions, language references
3. **Read existing tests** — understand what's already covered and what patterns are used
4. **Run the reference system** (if one exists) — capture actual behavior
5. **Enumerate systematically** — list every feature, variant, edge case, and combination

The depth of exploration scales with how much is already known. If an external system provides all the answers, this step is lightweight. If the reference must be constructed from docs and source code, this step is the most important one.

Output: a comprehensive feature inventory that becomes the basis for SCENARIOS.md.

### Step 3: Chart the Starmap

Decompose into scenarios following ./scenarios-template.md. Structure: phases (ordered by dependency) > sections (independent within phase, 5-25 scenarios each) > scenarios (concrete, binary pass/fail).

### Step 4: Generate Skills

Generate a **worker** skill (./worker-template.md) and a **driver** skill (./driver-template.md), customized for the project's test patterns, verification commands, and commit conventions.

### Step 5: Review

Dispatch a fresh review subagent using ./reviewer-prompt.md before execution begins.

### Step 6: Execute

Use the generated driver skill: `status`, `plan`, `next`, `run X.Y`, `run-all`, `report`.

## Key Principles

1. **SCENARIOS.md is the source of truth** — checkboxes ARE the progress
2. **Expectations are authoritative once reviewed** — whether from an external system, docs, or agent analysis, once reviewed and committed, don't weaken them to match implementation
3. **One section at a time** — focused unit of work with its own commit
4. **Progress is monotonic** — once a scenario passes, it never regresses

## Anti-Patterns

- **Scenarios too vague**: "handle all numeric types" — each type should be separate
- **Worker doing too much**: if 20+ scenarios fail, fix 5-10, commit, let driver re-dispatch the rest
- **Skipping exploration**: jumping to scenarios without understanding the territory leads to gaps
- **Unreviewed expectations**: agent-generated expectations must be reviewed before becoming authoritative
- **Not updating SCENARIOS.md**: progress is invisible if checkboxes aren't updated
