# Driver Skill Template

Generate a driver skill at `~/.claude/skills/<project>-driver/SKILL.md` using this template. The driver manages progress and dispatches worker subagents — it never does implementation.

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

- **status** — Show progress per section (count checkboxes in SCENARIOS.md)
- **next** — Dispatch next pending section as a fresh subagent
- **run <section>** — Dispatch specific section as a fresh subagent
- **run-all** — Run all remaining pending sections sequentially (auto-pilot)
- **plan** — Show recommended execution order
- **report** — Full progress report

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
    SCENARIOS.md location: <path>
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
    - Only add NEW test cases for scenarios still marked [ ] in SCENARIOS.md
    - If all pending scenarios are already covered, skip to running tests

    ## Return Format
    After completing all steps (including commit), return a summary:
    - Section name
    - Scenarios passed: N/M
    - Fixes applied: <list>
    - Partial/skipped: <list with reasons>
  """
)

## run-all Command

Runs all remaining pending sections sequentially in plan priority order:
1. Identify all sections with [ ] pending, sort by plan priority
2. For each: dispatch subagent → print summary → show cumulative status
3. Stop on fatal failure (build broken); continue on partial ([~])
4. **Pause after every 10 sections** — report cumulative progress and ask user whether to continue
5. Resumable: re-running picks up where it left off (checkboxes are durable)

## Execution Rules

- One subagent at a time — don't parallelize
- Driver never does implementation — only dispatches and tracks
- Subagent must commit before returning
- All counts are dynamic — computed from SCENARIOS.md checkboxes, never hardcoded
```

## Customization Points

When generating the driver skill, replace these with project-specific details:

| Placeholder | Example |
|------------|---------|
| `<project>` | `mysql-catalog` |
| `<worker-skill-path>` | `~/.claude/skills/mysql-catalog-worker/SKILL.md` |
| `<path>` to SCENARIOS.md | `backend/plugin/catalog/mysql/SCENARIOS.md` |
| `<test-infrastructure-file>` | `oracle_test.go` |
| `<existing-test-file>` | `create_table_oracle_test.go` |
| Recommended execution order | Phase 1 first, then Phase 2 sections in any order |

## What Stays Where

| Main context (driver) | Subagent (worker) |
|------------------------|-------------------|
| `status` — read checkboxes | Read pending scenarios |
| `plan` — show order | Write oracle test cases |
| `next` — pick & dispatch | Run tests, analyze diffs |
| `report` — aggregate stats | Fix code, verify no regression |
| Track overall progress | Update checkboxes, commit |
