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

Coverage planning + proof-preserving parallelization for AI coding agents.

Not for tasks with fewer than 50 scenarios — use a regular implementation plan instead.

## The Process

```
/starmap init      → Interactive: define goal, generate SCENARIOS-<project>.md + worker + driver skills
```

### Step 1: Understand the Goal

If the user already stated the goal in their message, skip straight to exploration. Only ask "What is the goal?" when it's genuinely unclear.

Then explore autonomously — the agent can figure out where the project lives, what the verification surface is, and other context by reading code. Asking the user questions they'd expect you to answer yourself wastes their time and breaks trust.

### Step 2: Explore

Dispatch exploration subagents to build understanding across two dimensions:

**Feature terrain** — what must be covered:
1. Read source code — understand what the system does and what it should support
2. Read documentation — official specs, grammar definitions, language references
3. Read existing tests — what's already covered and what patterns are used
4. Run the reference system (if one exists) — capture actual behavior
5. Enumerate systematically — every feature, variant, edge case, and combination

**Change terrain** — what execution surfaces are involved:
1. Identify shared callers and dispatch layers — files imported by many modules
2. Identify shared test surfaces — test helpers, fixtures, shared test files
3. Identify integration hotspots — registries, routers, config files that multiple sections would touch
4. Note shared progress artifacts — the SCENARIOS file itself, shared state files

The change terrain exploration prevents the most common parallelization failure: treating topic-level separation as execution-level separation. Two sections about different features may still collide on the same shared caller file.

After exploration, present a **single proposal** to the user covering:

1. **What you found** — brief summary of current coverage and key gaps
2. **Reference strategy** — how to verify correctness
3. **Proposed scope** — phase/section outline with approximate scenario counts
4. **Change-surface overview** — are sections well-isolated or do they share significant files?

This is the one confirmation checkpoint. Once the user confirms, proceed to chart.

### Step 3: Chart the Starmap

Decompose into scenarios following ./scenarios-template.md. Structure: phases (ordered by dependency) > sections (independent within phase, 5-25 scenarios each) > scenarios (concrete, binary pass/fail).

For each section, annotate the change surface: which files it will likely modify (Targets), any files shared with other sections (Shared), and its proof command (Proof). These annotations can be shallow ("Shared: none") for obviously simple sections — the point is to never skip the question.

### Step 4: Generate Skills

Generate a **worker** skill (./worker-template.md) and a **driver** skill (./driver-template.md), customized for the project's test patterns, verification commands, and commit conventions.

### Step 5: Review

Dispatch a fresh review subagent using ./reviewer-prompt.md. The review now covers completeness, structure, change-surface annotations, and proof boundaries.

### Step 6: Design Execution (per phase)

Before executing each phase, dispatch a fresh subagent using ./execution-design-prompt.md to produce an execution plan. This agent gets a clean context — its only job is execution architecture.

It reads the change-surface annotations from SCENARIOS, verifies them against the actual codebase, and classifies the phase into an execution shape:

- **Sequential** — deep coupling or shared surfaces that can't be prepped away
- **Prep-gated** — a preparation step (shared scaffolding, stubs, interface changes) unlocks parallel execution
- **Parallel** — sections are independent on all three dimensions
- **Integration-only** — sections run in parallel but need a dedicated integration step afterward

It also defines proof checkpoints: section-local proof (worker verifies), batch integration proof (driver verifies after merge), and global proof (phase-end full verification).

This step is always performed but may be shallow. For phases with 3 or fewer clearly-isolated sections, a one-line plan suffices: "Sequential, standard proof, no shared surfaces."

### Step 7: Execute

Use the generated driver skill: `status`, `plan`, `next`, `run X.Y`, `run-all`, `report`.

Execution follows the staged verification model:
- **Section-local proof**: each worker verifies its own tests pass before returning
- **Batch integration proof**: after each parallel batch, driver runs integration verification
- **Global proof**: at phase end, driver runs the full canonical build + test suite

## Key Principles

1. **SCENARIOS-<project>.md is the source of truth** — checkboxes ARE the progress
2. **Expectations are authoritative once reviewed** — never weaken them to match implementation
3. **One section at a time** — focused unit of work with its own commit
4. **Progress is monotonic** — once a scenario passes, it never regresses
5. **Three kinds of independence** — semantic (different features), change-surface (different files), proof (non-interfering verification). All three are needed for safe parallel execution.
6. **Heavy-by-default planning with pruning** — always ask the change-surface and proof questions, but allow shallow answers when the situation is obviously simple

## Anti-Patterns

- **Scenarios too vague**: "handle all numeric types" — break into one scenario per type, because vague scenarios can't be verified as pass/fail
- **Worker doing too much**: if 20+ scenarios fail, fix 5-10, commit, let driver re-dispatch the rest — small verified commits beat heroic efforts that break things
- **Skipping exploration**: jumping to scenarios without understanding the territory leads to gaps that are expensive to backfill later
- **Unreviewed expectations**: agent-generated expectations must be reviewed before becoming authoritative — a wrong expectation silently corrupts all downstream work
- **Not updating checkboxes**: progress is invisible if SCENARIOS-<project>.md isn't updated — the whole system depends on checkboxes being the single source of truth
- **Confusing semantic with change-surface independence**: two sections about different features may still collide on shared callers, dispatch layers, or test fixtures. Topic separation is not execution separation.
