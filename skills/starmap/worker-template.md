# Worker Skill Template

Generate a worker skill at `~/.claude/skills/<project>-worker/SKILL.md` using this template. Customize the test pattern, verification command, and commit format for the specific project.

```markdown
---
name: <project>-worker
description: Use when implementing a batch of <project> scenarios. Takes a section
  from SCENARIOS-<project>.md, writes tests, runs verification, fixes differences, reports results.
---

# <Project> Worker

Execute one section of scenarios.

## Usage

/<project>-worker <section>

## Process

1. Read SCENARIOS-<project>.md, extract pending scenarios for <section>
2. Read the section's change-surface annotations (Targets, Shared, Proof). Stay within the declared target files. If you need to modify a file not listed in Targets, note it in your return — this signals an annotation that needs updating.
3. Write test cases (table-driven, one case per scenario)
4. Determine expected results:
   - If an external system exists: run it to capture expected output
   - Otherwise: derive expectations from docs, specs, and source code analysis
5. Run tests, compare actual vs expected
6. For each failure, determine root cause:
   - Implementation wrong → fix implementation
   - Expectation wrong (based on deeper analysis) → fix expectation, document reasoning
7. **Review**: present any non-obvious or agent-derived expectations for review before committing
8. **Section-local proof**: run the section's Proof command from annotations (or the default test command if "standard"). This must pass before proceeding.
9. Report checkbox updates in your return format (which scenarios are [x] passing, [~] partial). The driver is responsible for updating SCENARIOS-<project>.md — workers never write to the SCENARIOS file directly.
10. Commit: stage specific files (implementation + tests only, NOT SCENARIOS) → commit with scenario stats

## Test Pattern

[Customize for the project. Example:]

- Table-driven tests with one entry per scenario
- Compare actual output against expected output
- Normalize whitespace/formatting before comparison

When dispatched as part of a parallel batch, write tests to a per-section file (e.g., `section_1_1_test.go`) instead of appending to the shared test file. The driver will merge these into the canonical test file after the batch completes.

## Commit Workflow

After each section completes:
1. Run section-local proof (the section's proof command, or tests scoped to this section's files). Full suite is the driver's responsibility at batch/global proof.
2. Stage only modified files by name (implementation + tests). Do NOT stage SCENARIOS-<project>.md — the driver updates it.
3. Commit with message: `feat(<project>): verify section X.Y — <name>`
4. Include scenario stats in commit body (N/M passing, any partial/skipped)
5. **Verify the commit exists** — run `git log --oneline -1` and include the commit SHA in your return. This is critical when running in a worktree: if you don't commit, the worktree is automatically cleaned up and your work is lost.

## Triage

If more than 10 scenarios fail in a section:
1. Fix up to 10, prioritizing the simplest/most foundational
2. Commit with progress so far
3. Mark remaining failures as [ ] (still pending)
4. Return to driver — it will re-dispatch this section later

Do not attempt to fix everything in one pass. Small, verified commits beat heroic efforts.

## Rules

- When running in a worktree, all file operations use the worktree directory as the working directory — never read or write files in the main repo path
- Once expectations are reviewed and committed, treat them as authoritative — fix implementation, not expectations
- If deeper analysis reveals an expectation was wrong, fix it with documented reasoning
- Run section-local proof after fixes — full test suite is the driver's job at batch/global proof
- One section per invocation
- One commit per section — don't accumulate multiple sections
- Never use `git add -A` or `git add .` — stage specific files only
- If a scenario needs upstream changes (parser, new dependency), mark [~] and move on
```

## Customization Points

When generating the worker skill, replace these with project-specific details:

| Placeholder | Example |
|------------|---------|
| `<project>` | `pg-completion` |
| Test pattern | Table-driven YAML tests with `\|` cursor marker |
| Expected results source | External system, docs analysis, source code analysis |
| Commit prefix | `test(pg-completion)` |
| Full test command | `go test ./backend/plugin/parser/pg/... -run Completion` |
