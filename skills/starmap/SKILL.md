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

## Three Stages

```
/starmap init  →  Plan  →  Design  →  ready to execute
```

Starmap works in three stages. Each stage has a clear deliverable and a user checkpoint before moving on.

| Stage | What happens | Deliverable |
|-------|-------------|-------------|
| **Plan** | Explore, enumerate scenarios, generate skills, review | SCENARIOS-<project>.md + worker + driver skills |
| **Design** | Analyze change surfaces, build execution contract | Execution contract written into driver skill |
| **Execute** | Run sections per contract, staged verification | Checkboxes + commits |

Re-entry: if returning to a project that already has SCENARIOS and skills, skip to Design (or Execute if a contract already exists).

---

## Stage 1: Plan

Goal: produce a reviewed SCENARIOS file and generated skills.

### 1.1 Understand the Goal

If the user already stated the goal in their message, skip straight to exploration. Only ask "What is the goal?" when it's genuinely unclear.

Then explore autonomously — the agent can figure out where the project lives, what the verification surface is, and other context by reading code. Asking the user questions they'd expect you to answer yourself wastes their time and breaks trust.

### 1.2 Explore

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

After exploration, present a **single proposal** to the user covering:

1. **What you found** — brief summary of current coverage and key gaps
2. **Reference strategy** — how to verify correctness
3. **Proposed scope** — phase/section outline with approximate scenario counts
4. **Change-surface overview** — are sections well-isolated or do they share significant files?

This is the Plan stage's confirmation checkpoint. Once the user confirms, proceed.

### 1.3 Chart

Decompose into scenarios following ./scenarios-template.md. Structure: phases (ordered by dependency) > sections (coverage units, 5-25 scenarios each) > scenarios (concrete, binary pass/fail).

For each section, annotate the change surface: Targets (files to modify), Shared (files shared with other sections), Proof (verification command). Annotations can be shallow ("Shared: none") for simple sections — the point is to never skip the question.

### 1.4 Generate Skills

Generate a **worker** skill (./worker-template.md) and a **driver** skill (./driver-template.md), customized for the project's test patterns, verification commands, and commit conventions.

### 1.5 Review

Dispatch a fresh review subagent using ./reviewer-prompt.md. Covers completeness, structure, change-surface annotations, and proof boundaries.

**Plan stage is complete.** Deliverable: SCENARIOS file + worker + driver skills.

---

## Stage 2: Design

Goal: produce an execution contract for Phase 1 (and later, for each subsequent phase before it runs).

Dispatch a fresh subagent using ./execution-design-prompt.md. This agent gets a clean context — its only job is execution architecture.

It reads the change-surface annotations from SCENARIOS, verifies them against the actual codebase, and classifies the phase into an execution shape:

- **Sequential** — deep coupling or shared surfaces that can't be prepped away
- **Prep-gated** — a preparation step (stubs, scaffolding, interface changes) unlocks parallel execution
- **Parallel** — sections are independent on all three dimensions
- **Integration-only** — sections run in parallel but need a dedicated integration step afterward

It outputs a structured execution contract (UNIT/BATCH/PREP/PROOF format) that gets written into the driver skill's `## Execution Contract` section, replacing any previous contract.

For Phase 1, this happens during `/starmap init`. For Phase 2+, the driver dispatches a new design agent before starting each phase — because earlier phases change the codebase, so each design must be based on the latest state.

**Design stage is complete when the driver skill has an execution contract.** The driver will not execute without one.

---

## Stage 3: Execute

Use the generated driver skill: `status`, `plan`, `next`, `run X.Y`, `run-all`, `report`.

The driver follows the execution contract exactly. It cannot override batch ordering or parallelism decisions — to change the plan, it must dispatch a new design agent and replace the contract.

Execution follows the staged verification model:
- **Section-local proof**: each worker verifies its own tests pass before returning
- **Batch integration proof**: after each parallel batch, driver merges worktree branches and runs integration verification
- **Global proof**: at phase end, driver runs the full canonical build + test suite

When a phase completes, the driver returns to Stage 2 to design the next phase, then resumes Stage 3.

---

## Key Principles

1. **SCENARIOS-<project>.md is the source of truth** — checkboxes ARE the progress
2. **Expectations are authoritative once reviewed** — never weaken them to match implementation
3. **One section at a time** — focused unit of work with its own commit
4. **Progress is monotonic** — once a scenario passes, it never regresses
5. **Three kinds of independence** — semantic (different features), change-surface (different files), proof (non-interfering verification). All three are needed for safe parallel execution.
6. **Design before execute** — no phase runs without an execution contract

## Anti-Patterns

- **Scenarios too vague**: "handle all numeric types" — break into one scenario per type, because vague scenarios can't be verified as pass/fail
- **Worker doing too much**: if 10+ scenarios fail, fix up to 10, commit, let driver re-dispatch the rest — small verified commits beat heroic efforts that break things
- **Skipping exploration**: jumping to scenarios without understanding the territory leads to gaps that are expensive to backfill later
- **Skipping Design stage**: going straight from Plan to Execute means defaulting to sequential — you lose parallelization opportunities and the change-surface analysis that prevents conflicts
- **Confusing semantic with change-surface independence**: two sections about different features may still collide on shared callers, dispatch layers, or test fixtures. Topic separation is not execution separation.
