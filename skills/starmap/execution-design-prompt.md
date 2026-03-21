# Execution Design Prompt Template

Before executing each phase, dispatch a fresh subagent with this prompt to design the execution architecture. This agent gets a clean context — its only job is to determine how sections should be executed while preserving coverage and correctness.

```
Agent(
  description: "Design execution for phase N",
  prompt: """
    You are designing the execution architecture for one phase of a starmap.

    ## Input
    1. SCENARIOS file at <path> — read the sections in Phase N, including their change-surface annotations (Targets, Shared, Proof)
    2. The codebase — read the actual source files to verify annotations
    3. Execution log at <log-path> (if exists) — actual files_modified from prior phases
    4. The change-surface annotations per section (Targets, Shared, Proof fields)

    ## Your Task

    ### Step 1: Verify change-surface annotations
    Read each section's Targets/Shared annotations. Check them against the actual codebase (imports, callers, function references). Update if wrong. This is the foundation — everything downstream depends on accurate annotations.

    ### Step 2: Classify three kinds of independence
    For each pair of sections in this phase, assess:
    - **Semantic independence**: different features/concepts (almost always yes for different sections)
    - **Change-surface independence**: no shared files in Targets (check the Shared annotations)
    - **Proof independence**: one section's test results cannot be invalidated by the other's changes

    All three must hold for safe parallel execution.

    ### Step 3: Choose execution shape
    Classify the phase into one of:
    - **Sequential**: sections have deep coupling or shared surfaces that can't be prepped away
    - **Prep-gated**: a preparation step (stubs, shared scaffolding, interface changes) breaks the dependency chain and unlocks parallel execution. Only worth it when prep unlocks 3+ parallel sections.
    - **Parallel**: sections are independent on all three dimensions — batch them
    - **Integration-only**: sections can run in parallel but require a dedicated integration step afterward (shared test surface, coordinated caller update)

    ### Step 4: Define proof checkpoints
    - **Section-local proof**: what each worker verifies (usually its own tests pass)
    - **Batch integration proof**: what the driver verifies after merging a parallel batch (full test suite, or a targeted subset). Only needed for parallel batches.
    - **Global proof**: what the driver runs at phase end (canonical build + full test suite). Always required.

    ### Step 5: Output the execution design

    Format:
    ```
    ## Phase N Execution Design

    ### Execution Shape: <sequential | prep-gated | parallel | integration-only>

    ### Change-Surface Summary
    - Section X.1: targets [a.go] — shared: none
    - Section X.2: targets [c.go] — shared: none
    - Section X.3: targets [a.go, b.go] — shared: a.go (with X.1)

    ### Preparation (if prep-gated)
    - Description: <what mechanical change to make>
    - Success criterion: <e.g., code compiles>

    ### Batch Plan
    - Batch 1 (parallel): X.1, X.2
    - Batch 2 (sequential): X.3 — shares a.go with X.1

    ### Proof Checkpoints
    - Section-local: <command>
    - Batch integration: <command> (after each parallel batch)
    - Global: <command> (at phase end)

    Estimated: N sections in M batches (vs N sequential)
    ```

    ## Rules
    - Be conservative: if unsure whether two sections conflict, keep them sequential
    - Read actual source files to verify dependencies — don't guess from section names alone
    - A preparation step is only worth it when it unlocks 3+ parallel sections
    - The design does NOT change what scenarios exist — only execution order and grouping
    - Never skip the three-independence check, even when it's obviously simple — state the result
  """
)
```

## When to Go Shallow

This step is always performed, but depth scales with phase complexity:

- **3 or fewer sections, all Shared: none**: one-line plan — "Sequential, standard proof. No shared surfaces."
- **Phase with clear prep opportunity** (e.g., signature migration): full prep-gated design
- **Phase with many independent sections**: full parallel batching plan
- **User explicitly asks to skip**: fall back to sequential execution
