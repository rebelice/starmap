# Starmap Reviewer Prompt Template

Dispatch a fresh review subagent with this prompt **before** starting execution. The reviewer has NO prior context — it reads everything fresh and evaluates independently.

**Purpose:** Catch gaps, structural issues, and sizing problems before spending hours executing a flawed plan.

Dispatch using your platform's subagent mechanism (e.g., Agent tool in Claude Code):

```
Agent(
  description: "Review starmap decomposition",
  prompt: """
    You are reviewing a starmap (scenario-driven development plan). Read the
    following files and evaluate whether the decomposition is sound:

    1. SCENARIOS.md at <path> — the master scenario list
    2. Worker skill at <worker-skill-path>
    3. Driver skill at <driver-skill-path>

    Evaluate and report on:

    **Completeness:**
    - Are there obvious gaps? Missing feature areas, edge cases, or error scenarios?
    - Does the scenario count feel right for the scope? (200-500 is typical)
    - Are all variants of each feature enumerated (not just happy path)?

    **Structure:**
    - Are phases ordered by dependency? (Can Phase 2 be done without Phase 1?)
    - Are sections within a phase truly independent?
    - Is each scenario concrete and binary (pass/fail, not "mostly works")?
    - Are scenarios named by what they test, not how?

    **Granularity:**
    - Too coarse? (e.g., "all numeric types" as one scenario)
    - Too fine? (e.g., separate scenarios for trivially similar cases)
    - Are sections sized reasonably? (5-25 scenarios each)

    **Worker/Driver fit:**
    - Does the worker process match the verification surface?
    - Does the commit workflow make sense for the batch size?
    - Are the driver commands sufficient to manage the work?

    **Reference quality:**
    - Are the reference sources sufficient for this goal?
    - Are there areas where expectations are especially uncertain and need careful review?
    - Is the verification strategy clear and reproducible?

    **Output format:**
    - Approved — no significant issues
    - Suggestions — list specific improvements (add scenario X, merge sections Y and Z)
    - Rework needed — fundamental issues that must be fixed before starting

    Be specific. Don't say "consider adding more edge cases" — say "Section 1.1 is
    missing LATERAL JOIN and recursive CTE scenarios."
  """
)
```

## When to Skip Review

You may skip review only if:
- The starmap has fewer than 50 scenarios (small scope)
- The user explicitly asks to skip
- This is a re-review after incorporating previous feedback

In all other cases, review is mandatory. 15 minutes of review saves hours of rework.
