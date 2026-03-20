# Optimize Prompt Template

Before executing each phase, dispatch a fresh subagent with this prompt to produce an execution plan. The optimizer has a clean context — its only job is to maximize parallelism without breaking correctness.

```
Agent(
  description: "Optimize phase N execution plan",
  prompt: """
    You are analyzing a starmap phase to find the best parallel execution strategy.

    ## Input
    1. SCENARIOS file at <path> — read the sections in Phase N
    2. The codebase — read the source files referenced by each section
    3. Execution log at <log-path> (if exists) — actual files_modified from prior phases

    ## Your Task

    For each section in this phase, determine:
    - Which source files it will modify (read the scenario descriptions + the actual source files)
    - Which source files it depends on (check import graph)

    Then build an execution plan:

    ### Step 1: Build dependency graph
    - Section X.Y targets files [a.go, b.go]
    - Section X.Z targets files [c.go, d.go]
    - If they share no files → can run in parallel
    - If they share files → must be sequential

    ### Step 2: Identify parallelization patterns
    - **Independent sections**: no shared target files → batch together
    - **Dependency chain**: section A changes interfaces that section B calls →
      consider a preparation step (mechanical stub pass) to break the chain
    - **Resource conflicts**: sections that use external resources (DB, APIs) →
      can they be isolated with per-section namespaces? If not, keep sequential

    ### Step 3: Output the execution plan

    Format:
    ```
    ## Phase N Execution Plan

    ### Preparation (if needed)
    - Mechanical stub pass: [description of what to do]
    - Success criterion: code compiles

    ### Batch 1 (parallel)
    - Section X.1: targets [a.go]
    - Section X.2: targets [c.go]
    - Section X.3: targets [e.go]

    ### Batch 2 (parallel)
    - Section X.4: targets [b.go]
    - Section X.5: targets [d.go]

    ### Batch 3 (sequential — shared dependency)
    - Section X.6: targets [a.go, b.go] — conflicts with batch 1

    Estimated speedup: N sections in M batches (vs N sequential)
    ```

    ## Rules
    - Be conservative: if unsure whether two sections conflict, keep them sequential
    - Read actual source files to verify dependencies — don't guess from section names alone
    - A preparation step (stub pass) is only worth it when it unlocks 3+ parallel sections
    - The plan does NOT change what scenarios exist — only execution order and grouping
  """
)
```

## When to Skip

Skip optimization when:
- The phase has 3 or fewer sections (not worth the analysis overhead)
- All sections are clearly independent (no shared code paths)
- The user explicitly asks to skip
