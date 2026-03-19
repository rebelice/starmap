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

### Step 1: Understand the Goal

**One question: What is the goal?**

Ask this single open-ended question. This is the one thing only the user knows. Examples: "match MySQL 8.0 catalog behavior", "comprehensive completion tests for PG parser".

Then **the agent explores autonomously** — do NOT ask the user where the project lives, what the verification surface is, or other questions the agent can answer by reading code.

### Step 2: Explore & Propose

Dispatch exploration subagents to build a thorough understanding of the territory:

1. **Read source code** — understand what the system does and what it should support
2. **Read documentation** — official specs, grammar definitions, language references
3. **Read existing tests** — understand what's already covered and what patterns are used
4. **Run the reference system** (if one exists) — capture actual behavior
5. **Enumerate systematically** — list every feature, variant, edge case, and combination

The depth of exploration scales with how much is already known.

After exploration, present findings and the **one real decision** to the user:

**Propose a reference strategy** — lead with a recommendation and reasoning, then offer alternatives conversationally:

> I explored X and found Y. For verifying correctness, I'd recommend **running against [reference system]** because it gives us ground truth without ambiguity.
>
> Alternatively:
> - **Derive from docs/specs** — if no reference system is available, authoritative docs work well
> - **Analyze source code** — when building the reference from implementation knowledge
> - **Combine approaches** — e.g., run reference system for common cases, check docs for edge cases
>
> Which approach fits best?

This is the key decision point — everything else the agent should figure out autonomously.

### Step 3: Chart the Starmap

Decompose into scenarios following ./scenarios-template.md. Structure: phases (ordered by dependency) > sections (independent within phase, 5-25 scenarios each) > scenarios (concrete, binary pass/fail).

**Present the proposed scope before writing SCENARIOS.md** — show the phase/section outline with approximate scenario counts:

> Here's the structure I'd propose:
> - **Phase 1: Foundations** (~40 scenarios) — basic types, simple queries, ...
> - **Phase 2: Advanced** (~60 scenarios) — subqueries, joins, ...
> - Total: ~100 scenarios across 8 sections
>
> Does this coverage look right, or should I adjust the scope?

Once confirmed, write the full SCENARIOS.md.

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
