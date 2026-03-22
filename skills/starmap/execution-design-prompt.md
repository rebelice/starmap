# Execution Design Prompt Template

Before executing each phase, dispatch a fresh subagent with this prompt to design the execution architecture. The output is a **binding execution contract** — the driver must follow it exactly, not treat it as a suggestion.

```
Agent(
  description: "Design execution for phase N",
  prompt: """
    You are designing the execution architecture for one phase of a starmap.
    Your output is a binding contract — the driver will follow it exactly.

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

    ### Step 5: Output the execution contract

    Use this EXACT format — the driver parses it mechanically:

    ```
    # EXECUTION CONTRACT — Phase N

    ## Work Units
    - UNIT A1: sections [2.1, 2.2] — SEQUENTIAL within unit (shared parseComparison in expr.go)
    - UNIT A2: sections [2.3] — single section
    - UNIT A3: sections [2.4] — single section
    - UNIT B1: sections [2.5, 2.6] — SEQUENTIAL within unit (shared parseSelectStmt in select.go)
    - UNIT C1: sections [2.7] — single section
    - UNIT C2: sections [2.8] — single section

    ## Batch Plan
    - BATCH 1 (PARALLEL): units [A1, A2, A3, B1, C1, C2]
    - BATCH 2 (SEQUENTIAL): units [D1] — depends on BATCH 1 output

    ## Preparation (if any)
    - PREP: <description> — success criterion: <e.g., code compiles>
    - or: NONE

    ## Proof
    - SECTION-LOCAL (default): <command>
    - SECTION-LOCAL (overrides): UNIT A1: <command>, UNIT C4: <command>
    - BATCH-INTEGRATION: <command>
    - GLOBAL: <command>

    ## Estimated
    - Work units: N
    - Batches: M
    - Max parallelism: P
    ```

    ## Rules
    - Be conservative: if unsure whether two sections conflict, keep them sequential
    - Read actual source files to verify dependencies — don't guess from section names alone
    - A preparation step is only worth it when it unlocks 3+ parallel sections
    - The contract does NOT change what scenarios exist — only execution order and grouping
    - Never skip the three-independence check, even when it's obviously simple — state the result
    - Sections that share functions within the same file MUST be in the same work unit as SEQUENTIAL
  """
)
```

## After Design: Update the Driver

The execution contract must be written into the driver skill's `## Execution Contract` section, **replacing** any previous contract. There must be exactly one contract at any time — no old contracts lingering alongside new ones.

## Replanning

If the driver needs to deviate from the contract during execution (e.g., a batch fails and the dependency graph changes), it must:
1. Stop execution
2. Dispatch a new execution design subagent for the remaining work
3. Replace the old contract with the new one
4. Resume execution under the new contract

The driver cannot override the contract implicitly. Any change requires an explicit replan.

## When to Go Shallow

This step is always performed, but depth scales with phase complexity:

- **3 or fewer sections, all Shared: none**: use the same EXACT format but with a single batch, e.g., one UNIT per section, one BATCH (SEQUENTIAL), PREP: NONE, default proof commands
- **Phase with clear prep opportunity** (e.g., signature migration): full prep-gated design
- **Phase with many independent sections**: full parallel batching plan
- **User explicitly asks to skip**: fall back to sequential execution
