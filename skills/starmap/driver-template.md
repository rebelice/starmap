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

- **status** — Show progress per section. Read SCENARIOS-<project>.md with the Read tool and count checkboxes (`- [x]` = pass, `- [~]` = partial, `- [ ]` = pending) per section. Do NOT use shell commands (awk/gawk/sed) to parse — use the Read tool and count in your response.
- **next** — Dispatch next pending section as a fresh subagent
- **run <section>** — Dispatch specific section as a fresh subagent
- **run-all** — Run all remaining pending sections (auto-pilot). Batches obviously independent sections in parallel when safe, otherwise sequential.
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
  """
)

## run-all Command

Runs all remaining pending sections in plan priority order:
1. Identify all sections with [ ] pending, sort by plan priority
2. Group sections within the same phase into parallel batches (2-3 sections per batch) when they are clearly independent (different implementation targets, no shared code paths). When in doubt, keep them sequential.
3. For each batch:
   - If batch size = 1: dispatch single subagent as usual
   - If batch size > 1: dispatch all subagents in the batch simultaneously. Each worker writes tests to a per-section test file (e.g., `section_1_1_test.go`). Workers still commit individually.
   - After all workers in the batch complete, merge per-section test files into the canonical test file, remove the per-section files, and commit the merge.
4. Stop on fatal failure (build broken); continue on partial ([~])
5. Print cumulative progress summary after every 10 sections, but keep going — do not pause or ask for confirmation
6. Resumable: re-running picks up where it left off (checkboxes are durable)

## Execution Log

After each section completes, append a record to `STARMAP-LOG-<project>.json` in the project directory:

```json
{
  "section": "2.3",
  "section_name": "Comparison Operators",
  "phase": 2,
  "started_at": "2026-03-20T10:15:00Z",
  "finished_at": "2026-03-20T10:28:30Z",
  "duration_seconds": 810,
  "total_tokens": 45200,
  "scenarios_total": 8,
  "scenarios_passed": 7,
  "scenarios_partial": 1,
  "scenarios_pending": 0,
  "files_modified": ["mysql/deparse/expr.go", "mysql/deparse/expr_test.go"],
  "commit_sha": "a1b2c3d",
  "retry_count": 0,
  "batch_id": 3,
  "parallel_with": ["2.1", "2.2"],
  "outcome": "success",
  "error_summary": null
}
```

Fields: `phase` for phase-level aggregation, `total_tokens` from the Agent tool's return value for cost analysis, `commit_sha` for tracing which commit a section produced, `error_summary` for diagnosing failures (null when successful).

This log enables post-hoc analysis: identifying slow sections, cost hotspots, validating parallelization decisions, and tracing issues to specific commits.

## Execution Rules

- Default is sequential. Only batch sections within the same phase when independence is obvious.
- Driver never does implementation — only dispatches and tracks
- Subagent must commit before returning
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
| Recommended execution order | Phase 1 first, then Phase 2 sections in any order |

## What Stays Where

| Main context (driver) | Subagent (worker) |
|------------------------|-------------------|
| `status` — read checkboxes | Read pending scenarios |
| `plan` — show order | Write reference test cases |
| `next` — pick & dispatch | Run tests, analyze diffs |
| `report` — aggregate stats | Fix code, verify no regression |
| Track overall progress | Update checkboxes, commit |
