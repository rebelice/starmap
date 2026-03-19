# Starmap

Chart a complete map of every scenario between where you are and where you need to be, then navigate there one section at a time.

Starmap is an agent skill for systematic goal decomposition. It takes a large, ambitious goal — like "match the behavior of system X" or "support all features of Y" — and breaks it down into hundreds of concrete, verifiable scenarios. Then it generates project-specific worker and driver skills to execute them methodically.

## How It Works

1. **Chart** — Define your goal, reference system, and verification method. Starmap guides you through decomposing it into 200-500 concrete scenarios organized by dependency.

2. **Review** — A fresh subagent audits your starmap for completeness, structural issues, and gaps before you invest execution time.

3. **Navigate** — A generated driver skill dispatches worker subagents section by section. Each worker writes reference tests, fixes differences, updates scenario checkboxes, and commits. The driver tracks cumulative progress.

4. **Arrive** — Every scenario checkbox is a verified point on the map. When the starmap is fully checked, you've reached your destination.

## When to Use

- **Compatibility projects**: "make X behave identically to Y"
- **Coverage projects**: "support all features of Z"
- **Migration projects**: "migrate from A to B completely"
- Any goal where progress = "how many concrete scenarios pass against a reference"

**Not for:** tasks with fewer than 50 scenarios (use a regular implementation plan) or tasks without a clear reference system to verify against.

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

## Usage

```
/starmap init       — Interactive: define goal, create SCENARIOS.md, generate worker + driver
```

Then use the generated driver:

```
/project-driver status    — Progress per section
/project-driver plan      — Recommended execution order
/project-driver next      — Execute next pending section
/project-driver run-all   — Auto-pilot all remaining sections
```

See [examples/](examples/) for a concrete worked example.

## What Gets Generated

When you run `/starmap init`, three artifacts are created:

| Artifact | Location | Purpose |
|----------|----------|---------|
| **SCENARIOS.md** | In your project directory | The starmap — every scenario with a checkbox |
| **Worker skill** | `~/.claude/skills/<project>-worker/` | Executes one section: write tests, run reference, fix diffs, commit |
| **Driver skill** | `~/.claude/skills/<project>-driver/` | Manages progress, dispatches workers, tracks completion |

## Key Principles

1. **SCENARIOS.md is the source of truth** — checkboxes ARE the progress
2. **Reference is authoritative** — never adjust expectations to match implementation
3. **One section at a time** — focused unit of work with its own commit
4. **Progress is monotonic** — once a scenario passes, it never regresses
5. **Partial is OK** — `[~]` means "needs upstream work", track it, don't block

## Integration with Superpowers

Starmap complements [Superpowers](https://github.com/obra/superpowers) — Superpowers gives your agent power, Starmap gives it direction. Use Superpowers skills for individual task execution (TDD, code review, debugging) and Starmap for the large-scale goal decomposition layer above.

## License

MIT License — see [LICENSE](LICENSE) file for details.
