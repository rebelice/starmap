# Starmap

You tell your AI agent: "make our JSON formatter match `jq` exactly." Simple enough goal. But what does "exactly" actually mean? Hundreds of edge cases — numeric precision, unicode escapes, key ordering, nested indentation, trailing commas. Your agent fixes a few, misses dozens more, and you have no idea how far along you really are.

Starmap solves this. It forces your agent to enumerate *every* scenario upfront, then work through them one by one with a checkbox for each. You always know exactly where you stand. And when the work is large enough, Starmap analyzes file-level dependencies to safely parallelize sections — without breaking the build or losing proof of correctness.

## How It Works

You start with `/starmap init` and describe your goal. That's it — one question.

Your agent then goes and reads the code, the docs, the existing tests. It comes back with a proposal: "here's what I found, here's how I'd verify correctness, and here's the 170 scenarios I think we need to cover across 13 sections. Does this look right?"

Once you say go, Starmap generates a `SCENARIOS-<project>.md` file — your map — plus a pair of project-specific driver and worker skills.

Before each phase executes, a dedicated subagent analyzes which sections can safely run in parallel by checking file-level dependencies. It produces an execution contract: which sections are batched together, which must run sequentially, and what proof checkpoints to run after each batch. The driver follows this contract exactly.

Each worker writes tests, checks them against the reference, fixes what's broken, and commits. Parallel workers run in isolated git worktrees so they can build and test independently. After a batch completes, the driver merges the work, runs integration proof, and updates the checkboxes. You can watch, step in, or let it run on autopilot.

```
/json-formatter-driver status    → see exactly where you stand
/json-formatter-driver next      → execute the next pending section
/json-formatter-driver run-all   → let it go until it's done
```

Progress is never ambiguous. Open `SCENARIOS-json-formatter.md` and count the checkboxes:

```markdown
### 1.1 Primitive Values
- [x] null literal
- [x] true literal
- [x] positive integer
- [ ] float with exponent notation    ← still pending
- [~] string with null bytes          ← needs upstream fix
```

## When to Use

Starmap is built for goals with *lots* of concrete, verifiable scenarios:

- **Compatibility** — "make X behave identically to Y"
- **Coverage** — "comprehensively test all aspects of Z"
- **Migration** — "migrate from A to B completely"

If your goal has fewer than 50 scenarios, a regular implementation plan is enough. Starmap shines when there are hundreds.

## A Small Example

Say you're building a JSON formatter and want it to match `jq .` output byte-for-byte. Starmap decomposes this into 40 scenarios across 6 sections. After a few rounds of `/json-formatter-driver next`, the status looks like:

```
JSON Formatter — Status

| Sect | Section                  | Pass | Partial | Pending | Total |
|------|--------------------------|------|---------|---------|-------|
| 1.1  | Primitive Values         |   12 |       0 |       0 |    12 |
| 1.2  | Simple Structures        |    7 |       0 |       0 |     7 |
| 1.3  | Indentation              |    4 |       0 |       2 |     6 |
| 2.1  | Numeric Precision        |    0 |       0 |       4 |     4 |
| 2.2  | String Edge Cases        |    0 |       0 |       6 |     6 |
| 2.3  | Structural Edge Cases    |    0 |       0 |       5 |     5 |
|------|--------------------------|------|---------|---------|-------|
| ALL  | TOTAL                    |   23 |       0 |      17 |    40 |

Progress: 23/40 (57%)
```

Phase 1 is mostly done. Phase 2 hasn't started. Each section is one worker invocation — it writes the tests, runs both formatters, compares output, fixes differences, and moves on.

See [examples/json-formatter/](examples/json-formatter/) for the full scenario map.

## Installation

### Claude Code

Tell Claude Code:

```
Read https://raw.githubusercontent.com/rebelice/starmap/main/INSTALL.md and follow the instructions to install starmap
```

Or install manually:

```bash
git clone https://github.com/rebelice/starmap.git ~/.claude/skills/starmap-repo
ln -sf ~/.claude/skills/starmap-repo/skills/starmap ~/.claude/skills/starmap
```

### Any Agent (via [npx skills](https://github.com/vercel-labs/skills))

```bash
npx skills add rebelice/starmap
```

### Updating

Tell Claude Code:

```
Update starmap by pulling the latest changes in ~/.claude/skills/starmap-repo
```

### Uninstalling

Tell Claude Code:

```
Uninstall starmap by removing ~/.claude/skills/starmap and ~/.claude/skills/starmap-repo
```

## What Gets Generated

Running `/starmap init` creates three things, plus an execution contract per phase:

| Artifact | Purpose |
|----------|---------|
| **SCENARIOS-<project>.md** | The map — every scenario with a checkbox + change-surface annotations |
| **Worker skill** | Executes one section: write tests, verify against reference, fix, commit |
| **Driver skill** | Dispatches workers, follows execution contract, runs proof checkpoints |
| **Execution contract** | Per-phase plan: which sections are parallel, which sequential, what proof to run |

## Philosophy

- **Enumerate first, implement second** — know the full scope before writing a line of code
- **Checkboxes are truth** — `SCENARIOS-<project>.md` is the single source of progress, always up to date
- **Expectations don't bend** — once a scenario's expected result is reviewed, the implementation adapts to it, not the other way around
- **Monotonic progress** — scenarios never regress once passing
- **Three kinds of independence** — semantic (different features), change-surface (different files), proof (non-interfering verification). All three must hold before sections run in parallel.
- **Proof-preserving parallelization** — parallel execution is a constrained optimization, not a default. Section-local proof, batch integration proof, and global proof form a layered verification stack.

## Acknowledgments

Starmap's skill architecture and interaction patterns are inspired by [Superpowers](https://github.com/obra/superpowers). Superpowers handles individual tasks well — TDD, code review, debugging. Starmap picks up where that leaves off: when the problem is too large for a single plan and you need to systematically cover hundreds of scenarios.

## License

MIT — see [LICENSE](LICENSE) for details.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=rebelice/starmap&type=Date)](https://star-history.com/#rebelice/starmap&Date)
