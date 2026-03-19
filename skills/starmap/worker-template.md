# Worker Skill Template

Generate a worker skill at `~/.claude/skills/<project>-worker/SKILL.md` using this template. Customize the test pattern, verification command, and commit format for the specific project.

```markdown
---
name: <project>-worker
description: Use when implementing a batch of <project> scenarios. Takes a section
  from SCENARIOS-<project>.md, writes tests, runs verification, fixes differences, updates progress.
---

# <Project> Worker

Execute one section of scenarios.

## Usage

/<project>-worker <section>

## Process

1. Read SCENARIOS-<project>.md, extract pending scenarios for <section>
2. Write test cases (table-driven, one case per scenario)
3. Determine expected results:
   - If an external system exists: run it to capture expected output
   - Otherwise: derive expectations from docs, specs, and source code analysis
4. Run tests, compare actual vs expected
5. For each failure, determine root cause:
   - Implementation wrong → fix implementation
   - Expectation wrong (based on deeper analysis) → fix expectation, document reasoning
6. **Review**: present any non-obvious or agent-derived expectations for review before committing
7. Update SCENARIOS-<project>.md checkboxes ([x] for passing, [~] for partial)
8. Commit: run full test suite → stage specific files → commit with scenario stats

## Test Pattern

[Customize for the project. Example:]

- Table-driven tests with one entry per scenario
- Compare actual output against expected output
- Normalize whitespace/formatting before comparison

## Commit Workflow

After each section completes:
1. Run full short test suite to confirm no regressions
2. Stage only modified files by name (implementation + tests + SCENARIOS-<project>.md)
3. Commit with message: `feat(<project>): verify section X.Y — <name>`
4. Include scenario stats in commit body (N/M passing, any partial/skipped)

## Triage

If more than 10 scenarios fail in a section:
1. Fix up to 10, prioritizing the simplest/most foundational
2. Commit with progress so far
3. Mark remaining failures as [ ] (still pending)
4. Return to driver — it will re-dispatch this section later

Do not attempt to fix everything in one pass. Small, verified commits beat heroic efforts.

## Rules

- Once expectations are reviewed and committed, treat them as authoritative — fix implementation, not expectations
- If deeper analysis reveals an expectation was wrong, fix it with documented reasoning
- Always run full test suite after fixes to catch regressions
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
