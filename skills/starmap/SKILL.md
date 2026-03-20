---
name: starmap
description: Use this skill whenever the user needs to systematically cover a large
  feature area, match the behavior of a reference system, comprehensively test a complex
  subsystem, or tackle any goal where progress is measured by "how many concrete scenarios
  pass." Triggers on phrases like "match behavior of X", "full compatibility with Y",
  "comprehensive tests for Z", "migrate from A to B completely", or any task that
  clearly involves 50+ verifiable scenarios.
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
/starmap init      → Interactive: define goal, generate SCENARIOS-<project>.md + worker + driver skills
```

### Step 1: Understand the Goal

**One question: What is the goal?**

Ask this single open-ended question. This is the one thing only the user knows. Examples: "match MySQL 8.0 catalog behavior", "comprehensive completion tests for PG parser".

Then explore autonomously — the agent can figure out where the project lives, what the verification surface is, and other context by reading code. Asking the user questions they'd expect you to answer yourself wastes their time and breaks trust.

### Step 2: Explore & Propose

Dispatch exploration subagents to build a thorough understanding of the territory:

1. **Read source code** — understand what the system does and what it should support
2. **Read documentation** — official specs, grammar definitions, language references
3. **Read existing tests** — understand what's already covered and what patterns are used
4. **Run the reference system** (if one exists) — capture actual behavior
5. **Enumerate systematically** — list every feature, variant, edge case, and combination

The depth of exploration scales with how much is already known.

After exploration, present a **single proposal** to the user covering three things:

1. **What you found** — brief summary of current coverage and key gaps
2. **Reference strategy** — how to verify correctness. Lead with your recommendation and reasoning. If there's a genuine choice (e.g., external system available but docs also usable), present alternatives conversationally. If the choice is obvious (e.g., no external system exists), just state it — don't force a false decision.
3. **Proposed scope** — phase/section outline with approximate scenario counts

> **What I found:** 68 existing tests covering basic DML. Key gaps: DDL, window functions, ...
>
> **Reference strategy:** I'd recommend deriving expectations from the parser grammar rules + PostgreSQL docs, since there's no external completion engine to test against.
>
> **Proposed structure:**
> - **Phase 1: Foundation Gaps** (~45 scenarios) — join variants, advanced WHERE, ...
> - **Phase 2: DDL Contexts** (~50 scenarios) — CREATE, ALTER, DROP, ...
> - Total: ~170 scenarios across 13 sections
>
> Does this look right, or should I adjust anything?

This is the one confirmation checkpoint — keep it to a single message. Once the user confirms, proceed to chart the full SCENARIOS-<project>.md.

### Step 3: Chart the Starmap

Decompose into scenarios following ./scenarios-template.md. Structure: phases (ordered by dependency) > sections (independent within phase, 5-25 scenarios each) > scenarios (concrete, binary pass/fail).

### Step 4: Generate Skills

Generate a **worker** skill (./worker-template.md) and a **driver** skill (./driver-template.md), customized for the project's test patterns, verification commands, and commit conventions.

### Step 5: Review

Dispatch a fresh review subagent using ./reviewer-prompt.md before execution begins.

### Step 6: Execute

Use the generated driver skill: `status`, `plan`, `next`, `run X.Y`, `run-all`, `report`.

## Key Principles

1. **SCENARIOS-<project>.md is the source of truth** — checkboxes ARE the progress
2. **Expectations are authoritative once reviewed** — whether from an external system, docs, or agent analysis, once reviewed and committed, don't weaken them to match implementation
3. **One section at a time** — focused unit of work with its own commit
4. **Progress is monotonic** — once a scenario passes, it never regresses

## Anti-Patterns

- **Scenarios too vague**: "handle all numeric types" — break into one scenario per type, because vague scenarios can't be verified as pass/fail
- **Worker doing too much**: if 20+ scenarios fail, fix 5-10, commit, let driver re-dispatch the rest — small verified commits beat heroic efforts that break things
- **Skipping exploration**: jumping to scenarios without understanding the territory leads to gaps that are expensive to backfill later
- **Unreviewed expectations**: agent-generated expectations must be reviewed before becoming authoritative — a wrong expectation silently corrupts all downstream work
- **Not updating checkboxes**: progress is invisible if SCENARIOS-<project>.md isn't updated — the whole system depends on checkboxes being the single source of truth
