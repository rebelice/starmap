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
/starmap init  →  Coverage  →  Design  →  Execute
```

Each stage has one job, one deliverable, and a user checkpoint.

| Stage | Question | Deliverable |
|-------|----------|-------------|
| **Coverage** | What must be true? | SCENARIOS-<project>.md (pure scenarios, no implementation details) |
| **Design** | How to implement it fastest without losing correctness? | Worker + driver skills + execution contract |
| **Execute** | Do it. | Checkboxes + commits |

Re-entry: if returning to a project that already has SCENARIOS, skip to Design. If skills and contract already exist, skip to Execute.

---

## Stage 1: Coverage

Goal: a reviewed list of every scenario that must pass. Nothing about implementation — no file targets, no code architecture, no execution strategy.

### 1.1 Understand the Goal

If the user already stated the goal, skip straight to exploration. Only ask when genuinely unclear.

Explore autonomously — the agent can figure out where the project lives, what the verification surface is, and other context by reading code.

### 1.2 Explore

Dispatch exploration subagents to understand what must be covered:

1. Read source code — what the system does and should support
2. Read documentation — specs, grammar definitions, language references
3. Read existing tests — what's already covered and what patterns are used
4. Run the reference system (if one exists) — capture actual behavior
5. Enumerate systematically — every feature, variant, edge case, and combination

After exploration, present a **single proposal** to the user:

1. **What you found** — current coverage and key gaps
2. **Reference strategy** — how to verify correctness
3. **Proposed scope** — phase/section outline with approximate scenario counts

This is the Coverage stage's checkpoint. Once confirmed, proceed.

### 1.3 Chart

Decompose into scenarios following ./scenarios-template.md. Structure: phases (ordered by dependency) > sections (coverage units, 5-25 scenarios each) > scenarios (concrete, binary pass/fail).

No implementation details in SCENARIOS — no file targets, no shared annotations. Each scenario is a testable assertion about what the system should do, not how to implement it.

### 1.4 Review Coverage

Dispatch a fresh review subagent using ./reviewer-prompt.md. Reviews only coverage: completeness, structure, granularity, reference quality. Does not review implementation approach — that's Stage 2's job.

**Coverage stage is complete.** Deliverable: SCENARIOS-<project>.md.

---

## Stage 2: Design

Goal: given the scenario list, design the fastest correct implementation — code architecture, file structure, skills, parallelization, execution contract.

This stage makes all implementation decisions in one place, so architecture and parallelization are considered together.

### 2.1 Analyze the Implementation Space

Read the SCENARIOS file and the codebase (or assess the design space for greenfield projects). Decide:

**Code architecture:**
- For existing codebases: which files will each section modify?
- For greenfield: how should files be structured? Consider splitting by section to enable parallelism (e.g., `diff_schema.go`, `diff_table.go` instead of one `diff.go`)

**Change surfaces:**
- Which sections share files? Can the architecture be adjusted to reduce sharing?
- What are the integration hotspots (shared dispatch, registries, type definitions)?

**Parallelization:**
- Classify three kinds of independence: semantic, change-surface, proof
- Choose execution shape per phase: sequential, prep-gated, parallel, integration-only
- For prep-gated: define the preparation step (stubs, scaffolding, interface skeleton)

**Proof strategy:**
- Section-local proof commands
- Batch integration proof (for parallel batches)
- Global proof (phase-end full verification)

### 2.2 Generate Skills

Generate a **worker** skill (./worker-template.md) and a **driver** skill (./driver-template.md), customized for:
- The code architecture decided above
- File targets per section
- Test patterns and proof commands
- Commit conventions

### 2.3 Produce Execution Contract

Dispatch a fresh subagent using ./execution-design-prompt.md for Phase 1. It outputs a structured execution contract (UNIT/BATCH/PREP/PROOF format) written into the driver skill's `## Execution Contract` section.

For Phase 2+, the driver dispatches a new design agent before starting each phase — because earlier phases change the codebase.

### 2.4 Review Design

Present the implementation approach to the user: file structure, parallelization plan, execution contract. This is the Design stage's checkpoint.

**Design stage is complete.** Deliverable: worker skill + driver skill (with execution contract).

---

## Stage 3: Execute

Use the generated driver skill: `status`, `plan`, `next`, `run X.Y`, `run-all`, `report`.

The driver follows the execution contract exactly. It cannot override batch ordering or parallelism decisions — to change the plan, it must dispatch a new design agent and replace the contract.

Execution follows the staged verification model:
- **Section-local proof**: each worker verifies its own tests pass before returning
- **Batch integration proof**: after each parallel batch, driver merges worktree branches and runs integration verification
- **Global proof**: at phase end, driver runs the full canonical build + test suite

When a phase completes, the driver returns to Stage 2 (step 2.3) to design the next phase, then resumes Stage 3.

---

## Key Principles

1. **Coverage is king** — SCENARIOS-<project>.md defines what "done" means. Implementation details don't belong in it.
2. **Architecture serves parallelism** — code structure is a design decision, especially for greenfield projects. Choose structures that minimize shared files.
3. **Three kinds of independence** — semantic (different features), change-surface (different files), proof (non-interfering verification). All three needed for safe parallel execution.
4. **Design before execute** — no phase runs without an execution contract.
5. **Progress is monotonic** — once a scenario passes, it never regresses.

## Anti-Patterns

- **Scenarios too vague**: "handle all numeric types" — break into one scenario per type
- **Implementation details in SCENARIOS**: file targets, code architecture, execution strategy — these belong in Stage 2, not Stage 1
- **Defaulting to one big file**: for greenfield projects, putting everything in one file guarantees sequential execution. Split by section to enable parallelism.
- **Skipping Design**: going straight from Coverage to Execute means no architecture analysis, no parallelization, no execution contract
- **Confusing semantic with change-surface independence**: two sections about different features may still collide on shared files. Topic separation is not execution separation.
