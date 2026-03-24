# Coverage Review Prompt Template

Dispatch a fresh review subagent with this prompt at the end of Stage 1 (Coverage). The reviewer evaluates ONLY whether the scenario list is complete — not implementation approach, file structure, or execution strategy.

```
Agent(
  description: "Review starmap coverage",
  prompt: """
    You are reviewing a starmap's scenario coverage. Read the SCENARIOS file
    and evaluate whether it comprehensively covers the goal.

    SCENARIOS-<project>.md at <path>

    Evaluate ONLY coverage — do NOT evaluate implementation details
    (there shouldn't be any in the SCENARIOS file).

    **Completeness:**
    - Are there obvious gaps? Missing feature areas, edge cases, or error scenarios?
    - Does the scenario count feel right for the scope? (50-500 depending on project size)
    - Are all variants of each feature enumerated (not just happy path)?

    **Structure:**
    - Are phases ordered by dependency? (Can Phase 2 be done without Phase 1?)
    - Are sections properly scoped as coverage units?
    - Is each scenario concrete and binary (pass/fail, not "mostly works")?
    - Are scenarios named by what they test, not how to implement them?

    **Granularity:**
    - Too coarse? (e.g., "all numeric types" as one scenario)
    - Too fine? (e.g., separate scenarios for trivially similar cases)
    - Are sections sized reasonably? (5-25 scenarios each)

    **Reference quality:**
    - Are the reference sources sufficient for this goal?
    - Are there areas where expectations are especially uncertain?
    - Is the verification strategy clear and reproducible?

    **Contamination check:**
    - Does the SCENARIOS file contain file targets, code architecture, or
      execution strategy? If so, flag it — implementation details belong
      in Stage 2 (Design), not in SCENARIOS.

    **Output format:**
    - Approved — no significant issues
    - Suggestions — list specific improvements (add scenario X, merge sections Y and Z)
    - Rework needed — fundamental coverage gaps that must be fixed

    Be specific. Don't say "consider adding more edge cases" — say "Section 1.1 is
    missing LATERAL JOIN and recursive CTE scenarios."
  """
)
```

## When to Skip

- Fewer than 50 scenarios (small scope)
- User explicitly asks to skip
- Re-review after incorporating previous feedback
