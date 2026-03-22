# Driver Skill Template

Generate a driver skill at `~/.claude/skills/<project>-driver/SKILL.md` using this template. The driver manages progress, dispatches worker subagents, and performs integration edits (merging test files, updating SCENARIOS checkboxes). It never does section implementation.

```markdown
---
name: <project>-driver
description: Use when driving the <project> scenario coverage effort. Manages progress,
  dispatches worker subagents, tracks overall completion.
---

# <Project> Driver

## Usage

/<project>-driver <command>

## Commands

- **status** — Show progress per section. Read SCENARIOS-<project>.md with the Read tool and count checkboxes (`- [x]` = pass, `- [~]` = partial, `- [ ]` = pending) per section. Do NOT use shell commands (awk/gawk/sed) to parse — use the Read tool and count in your response.
- **next** — Dispatch next pending section as a fresh subagent
- **run <section>** — Dispatch specific section as a fresh subagent
- **run-all** — Run all remaining pending sections (auto-pilot). Follows the execution plan if one exists, otherwise sequential.
- **plan** — Show recommended execution order
- **report** — Full progress report. Same approach as `status` — read the file, count checkboxes, summarize.

## Subagent Dispatch

The `next` and `run` commands dispatch each section as a fresh subagent. Use your platform's subagent mechanism (e.g., Agent tool in Claude Code). Example prompt:

Agent(
  description: "Execute section X.Y",
  prompt: """
    You are a <project> worker. Execute section X.Y of the starmap.

    ## Instructions
    Read the worker skill at <worker-skill-path> and follow its process exactly.

    ## Task
    Section to execute: X.Y
    SCENARIOS-<project>.md location: <path>
    Project directory: <path>

    ## Existing Infrastructure
    Before writing any test code, read the existing test files to understand:
    - Test harness and helpers
    - How existing tests are structured (naming, patterns, imports)
    - Which test files exist and what sections they cover

    Key files to read first:
    - <test-infrastructure-file>
    - <existing-test-file>

    ## Re-entry Handling
    If a test function for this section already exists (from a prior partial run),
    do NOT create a duplicate. Instead:
    - Read the existing test function
    - Identify which test cases are already present
    - Only add NEW test cases for scenarios still marked [ ] in SCENARIOS-<project>.md
    - If all pending scenarios are already covered, skip to running tests

    ## Return Format
    After completing all steps (including commit), return a summary:
    - Section name
    - Scenarios passed: N/M
    - Fixes applied: <list>
    - Partial/skipped: <list with reasons>
    - Files modified: <list of all files you changed>
    - Shared files touched: <any files marked "Shared" in the section's annotations>
    - Proof result: pass/fail (did section-local proof pass?)
    - Commit SHA: <from git log --oneline -1>
    - Checkbox updates: <which scenarios to mark [x] or [~]>

    All file paths must be relative to the worktree root (when in worktree) or project root (when sequential). Do not reference the main repo path from inside a worktree.
  """
)

## run-all Command

Runs all remaining pending sections following the execution contract:
1. Identify all sections with [ ] pending
2. Read the execution contract (the `## Execution Plan` section in this skill file). If no contract exists, run sections sequentially in section-number order.
3. **Pre-dispatch consistency check**: before dispatching each batch, verify:
   - The work units in this batch match the contract exactly
   - Sections marked as SEQUENTIAL within a unit are dispatched to a single worker (not split)
   - No unit is dispatched that the contract says belongs to a later batch
   If any inconsistency is found, stop and replan — do not override the contract.
4. For each batch per the contract:
   a. Dispatch subagent(s):
      - **Sequential** (batch size = 1): dispatch single subagent without worktree isolation
      - **Parallel** (batch size > 1): dispatch all subagents simultaneously, each with `isolation: "worktree"`. Worktree is required for parallel execution because workers in the same directory break the build.
   b. **Verify worktree results** (parallel only): for each worker, check that the return includes a commit SHA. If missing (worktree cleaned up), the worker failed to commit — retry immediately.
   c. **Merge worktree branches** (parallel only): merge each worker's branch to main one at a time. After each merge, run a quick build check. If merge conflicts occur, classify and handle:
      - **Caller update conflict** (e.g., `stmt, err :=` vs `stmt, _ :=`): take the version with proper error handling (the one with `err`)
      - **Additive conflict** (both branches added code at the same insertion point): keep both additions, fix ordering if needed
      - **Structural conflict** (incompatible changes to the same function): stop and replan — the contract missed a dependency
      After all branches merged, merge per-section test files into the canonical test file, remove per-section files, and commit.
   d. **Batch integration proof** (parallel only): run the batch integration proof command. If it fails, identify which section caused the regression.
   e. Print section summary, then continue
4. **Global proof** at phase end: run the global proof command (canonical build + full test suite). This is mandatory — never skip.
5. Stop on fatal failure (build broken); continue on partial ([~])
6. Print cumulative progress summary after every 10 sections, but keep going — do not pause or ask for confirmation
7. Resumable: re-running picks up where it left off (checkboxes are durable)

## Proof Checkpoints

- **Section-local**: Worker runs its proof command before returning and reports pass/fail. Already implicit (workers run tests), but this is an explicit obligation.
- **Batch integration**: Driver runs integration proof after merging a parallel batch. Sequential sections skip this — section-local proof is sufficient.
- **Global**: Driver runs full proof at phase end. Mandatory — never skip.

## Execution Rules

- The execution contract is binding. The driver must not override batch ordering, unit composition, or parallelism decisions. To change the plan, dispatch a new execution design subagent and replace the contract.
- Driver never does section implementation — only dispatches, tracks, and performs integration edits (merging test files, updating SCENARIOS checkboxes, running proof commands)
- Subagent must commit before returning
- The driver is the sole writer of SCENARIOS-<project>.md checkboxes. Workers report results in their return format; driver applies checkbox updates after proof passes. This applies to both sequential and parallel execution.
- All counts are dynamic — computed from SCENARIOS-<project>.md checkboxes, never hardcoded
- Use the Read tool to parse SCENARIOS-<project>.md — do NOT use shell commands (awk/gawk/sed/python) for markdown parsing
```

## Customization Points

When generating the driver skill, replace these with project-specific details:

| Placeholder | Example |
|------------|---------|
| `<project>` | `mysql-catalog` |
| `<worker-skill-path>` | `~/.claude/skills/mysql-catalog-worker/SKILL.md` |
| `<path>` to SCENARIOS-<project>.md | `backend/plugin/catalog/mysql/SCENARIOS-<project>.md` |
| `<test-infrastructure-file>` | `reference_test.go` |
| `<existing-test-file>` | `create_table_reference_test.go` |
| Recommended execution order | Phase 1 first, then Phase 2; section order within each phase per execution design |

## What Stays Where

| Main context (driver) | Subagent (worker) |
|------------------------|-------------------|
| `status` — read checkboxes | Read pending scenarios |
| `plan` — show order | Write tests, fix implementation |
| `next` — pick & dispatch | Run section-local proof |
| `report` — aggregate stats | Commit implementation + tests |
| Update checkboxes, merge branches | Report results (never writes SCENARIOS) |
