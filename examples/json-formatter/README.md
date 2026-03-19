# Example: JSON Formatter Reference Compatibility

This is a worked example of a small starmap (~50 scenarios) for making a JSON formatter match `jq` output exactly.

## Goal Definition

| Question | Answer |
|----------|--------|
| **Goal** | JSON formatter output matches `jq .` behavior exactly |
| **Verification surface** | Byte-for-byte output comparison |
| **Reference system** | `jq .` command |
| **Project location** | `lib/json-formatter/` |

## Generated Artifacts

- **SCENARIOS.md** — 2 phases, 6 sections, ~50 scenarios
- **Worker skill** would be generated at `~/.claude/skills/json-formatter-worker/`
- **Driver skill** would be generated at `~/.claude/skills/json-formatter-driver/`

## Structure Notes

- **Phase 1** (Basic Formatting) must pass before Phase 2 (Edge Cases) — you can't test edge cases if basic formatting is wrong
- Sections within each phase are independent — 1.1, 1.2, 1.3 can be done in any order
- Each scenario is one specific input/output pair verified against `jq`

This is a small starmap. A real compatibility project (e.g., SQL dialect, API parity) would typically have 200-500 scenarios across 5-8 phases.
