# Worker Skill Template

Generate a worker skill at `~/.claude/skills/<project>-worker/SKILL.md` using this template. Customize the test pattern, verification command, and commit format for the specific project.

```markdown
---
name: <project>-worker
description: Use when implementing a batch of <project> scenarios. Takes a section
  from SCENARIOS.md, writes tests, runs verification, fixes differences, updates progress.
---

# <Project> Worker

Execute one section of scenarios.

## Usage

/<project>-worker <section>

## Process

### Mode A (external reference)

1. Read SCENARIOS.md, extract pending scenarios for <section>
2. Write test cases (table-driven, one case per scenario)
3. Run tests against reference system, capture expected output
4. For each failure: analyze diff → fix code → verify no regression
5. Update SCENARIOS.md checkboxes ([x] for passing, [~] for partial)
6. Commit: run full test suite → stage specific files → commit with scenario stats

### Mode B (derived reference)

1. Read SCENARIOS.md, extract pending scenarios for <section>
2. Write test cases (table-driven, one case per scenario)
3. Generate expected results based on exploration findings (docs, source code analysis, specs)
4. Run tests — if test fails, determine whether the expectation or the implementation is wrong:
   - Expectation wrong → fix the expectation, document the reasoning
   - Implementation wrong → fix the implementation
5. **Review checkpoint**: before committing, present the generated expectations for review
6. Update SCENARIOS.md checkboxes ([x] for passing, [~] for partial)
7. Commit: run full test suite → stage specific files → commit with scenario stats

## Test Pattern

[Customize for the project. Example:]

- Table-driven tests with one entry per scenario
- Reference comparison: run same input against reference system, compare output (Mode A)
- Generated expectations: agent produces expected output, human/agent reviews (Mode B)
- Normalize whitespace/formatting before comparison

## Commit Workflow

After each section completes:
1. Run full short test suite to confirm no regressions
2. Stage only modified files by name (implementation + tests + SCENARIOS.md)
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

- Mode A: never modify test expectations to match implementation — fix implementation
- Mode B: expectations can be corrected during review, but once reviewed and committed, treat them as authoritative
- Always run full test suite after fixes to catch regressions
- One section per invocation
- One commit per section — don't accumulate multiple sections
- Never use `git add -A` or `git add .` — stage specific files only
- If a scenario needs upstream changes (parser, new dependency), mark [~] and move on
```

## Customization Points

When generating the worker skill, replace these with project-specific details:

| Placeholder | Example (Mode A) | Example (Mode B) |
|------------|-------------------|-------------------|
| `<project>` | `mysql-catalog` | `pg-completion` |
| Test pattern | Table-driven Go tests with `startReference()` | Table-driven YAML tests with `|` cursor marker |
| Verification | Diff output against reference system | Agent-generated expectations, reviewed |
| Commit prefix | `feat(mysql-catalog)` | `test(pg-completion)` |
| Full test command | `go test ./backend/plugin/catalog/mysql/...` | `go test ./backend/plugin/parser/pg/... -run Completion` |
