# Starmap

You tell your AI agent: "make our JSON formatter match `jq` exactly." Simple enough goal. But what does "exactly" actually mean? Hundreds of edge cases — numeric precision, unicode escapes, key ordering, nested indentation, trailing commas. Your agent fixes a few, misses dozens more, and you have no idea how far along you really are.

Starmap solves this. It forces your agent to enumerate *every* scenario upfront, then work through them one by one with a checkbox for each. You always know exactly where you stand.

## How It Works

You start with `/starmap init` and describe your goal. That's it — one question.

Your agent then goes and reads the code, the docs, the existing tests. It comes back with a proposal: "here's what I found, here's how I'd verify correctness, and here's the 170 scenarios I think we need to cover across 13 sections. Does this look right?"

Once you say go, Starmap generates a `SCENARIOS-<project>.md` file — your map — plus a pair of project-specific driver and worker skills. The driver dispatches a fresh worker for each section. Each worker writes tests, checks them against the reference, fixes what's broken, ticks the checkboxes, and commits. You can watch, step in, or let it run on autopilot.

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

Say you're building a JSON formatter and want it to match `jq .` output byte-for-byte. Starmap would decompose this into something like:

**Phase 1: Basic Formatting** — primitives, simple structures, indentation rules
**Phase 2: Edge Cases** — numeric precision, string escapes, structural limits

Each phase breaks into sections (5-25 scenarios each), and each scenario is one specific, testable case: "negative zero formats the same way `jq` does." A worker picks up a section, writes the tests, runs both formatters, compares output, fixes differences, and moves on.

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

### Codex / Other Agents

```bash
git clone https://github.com/rebelice/starmap.git ~/.agents/skills/starmap-repo
ln -sf ~/.agents/skills/starmap-repo/skills/starmap ~/.agents/skills/starmap
```

### Updating

```bash
cd ~/.claude/skills/starmap-repo && git pull
```

The symlink means you always run the latest version.

### Uninstalling

```bash
rm ~/.claude/skills/starmap
rm -rf ~/.claude/skills/starmap-repo
```

## What Gets Generated

Running `/starmap init` creates three things:

| Artifact | Purpose |
|----------|---------|
| **SCENARIOS-<project>.md** | The map — every scenario with a checkbox |
| **Worker skill** | Executes one section: write tests, verify against reference, fix, commit |
| **Driver skill** | Dispatches workers, tracks progress, never does implementation itself |

## Philosophy

- **Enumerate first, implement second** — know the full scope before writing a line of code
- **Checkboxes are truth** — `SCENARIOS-<project>.md` is the single source of progress, always up to date
- **Expectations don't bend** — once a scenario's expected result is reviewed, the implementation adapts to it, not the other way around
- **Monotonic progress** — scenarios never regress once passing

## Integration with Superpowers

Starmap complements [Superpowers](https://github.com/obra/superpowers). Superpowers gives your agent power — TDD, code review, systematic debugging. Starmap gives it direction — decomposing an ambitious goal into hundreds of checkpoints and navigating through them. They work well together.

## License

MIT — see [LICENSE](LICENSE) for details.
