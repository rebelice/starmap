# Execution Design Prompt Template

Dispatch a fresh subagent with this prompt during Stage 2. The output is a **binding execution contract** — the driver must follow it exactly.

This agent handles the full Stage 2.1 + 2.3 scope: analyze the implementation space, determine file targets per section, design parallelization, and produce the execution contract.

```
Agent(
  description: "Design execution for phase N",
  prompt: """
    You are designing the execution architecture for one phase of a starmap.
    Your output is a binding contract — the driver will follow it exactly.

    ## Input
    1. SCENARIOS file at <path> — read the sections in Phase N (scenarios only, no implementation details)
    2. The codebase — read actual source files, imports, and module structure
    3. Execution log from prior phases (if any) — actual files_modified data
    4. Whether this is a greenfield implementation or modifying existing code

    ## Your Task

    ### Step 1: Determine file targets per section

    For each section in this phase, determine which files it will need to create or modify.

    **For existing codebases:** analyze the current code to identify which files each section's scenarios map to.

    **For greenfield projects:** design the file structure. Consider splitting into per-section or per-type files to enable parallelism. Putting everything in one file guarantees sequential execution — only do this when sections genuinely need to share state within the same file.

    Output a file-targets table:
    - Section X.1: targets [a.go, a_test.go]
    - Section X.2: targets [b.go, b_test.go]
    - Section X.3: targets [a.go, c_test.go] — shares a.go with X.1

    ### Step 2: Classify three kinds of independence
    For each pair of sections, assess based on the file targets from Step 1:
    - **Semantic independence**: different features/concepts (almost always yes)
    - **Change-surface independence**: no shared files in targets
    - **Proof independence**: one section's test results cannot be invalidated by the other's changes

    All three must hold for safe parallel execution.

    ### Step 3: Choose execution shape
    Classify the phase into one of:
    - **Sequential**: deep coupling or shared surfaces that can't be prepped away
    - **Prep-gated**: a preparation step (stubs, scaffolding, interface skeleton) breaks the dependency chain and unlocks parallel execution. Only worth it when prep unlocks 3+ parallel sections.
    - **Parallel**: sections are independent on all three dimensions — batch them
    - **Integration-only**: sections can run in parallel but need a dedicated integration step afterward

    ### Step 4: Define proof checkpoints
    - **Section-local proof**: what each worker verifies (usually its own tests pass)
    - **Batch integration proof**: what the driver verifies after merging a parallel batch. Only needed for parallel batches.
    - **Global proof**: what the driver runs at phase end (canonical build + full test suite). Always required.

    ### Step 5: Output the execution contract

    Use this EXACT format — the driver parses it mechanically:

    ```
    # EXECUTION CONTRACT — Phase N

    ## File Targets
    - SECTION 1.1: targets [schema.go, schema_test.go]
    - SECTION 1.2: targets [table.go, table_test.go]
    - SECTION 1.3: targets [table.go, column.go, column_test.go] — shares table.go with 1.2

    ## Work Units
    - UNIT A1: sections [1.1] — single section, targets [schema.go, schema_test.go]
    - UNIT A2: sections [1.2, 1.3] — SEQUENTIAL within unit (shared table.go)
    - UNIT B1: sections [1.4] — single section, targets [index.go, index_test.go]

    ## Batch Plan
    - BATCH 1 (PARALLEL): units [A1, A2, B1]
    - BATCH 2 (SEQUENTIAL): units [C1] — depends on BATCH 1

    ## Preparation (if any)
    - PREP: <description> — success criterion: <e.g., code compiles>
    - or: NONE

    ## Proof
    - SECTION-LOCAL (default): <command>
    - SECTION-LOCAL (overrides): UNIT A1: <command>, UNIT B1: <command>
    - BATCH-INTEGRATION: <command>
    - GLOBAL: <command>

    ## Estimated
    - Work units: N
    - Batches: M
    - Max parallelism: P
    ```

    ## Rules
    - All proof commands and file paths must be relative (e.g., `go test ./pg/catalog/...`), not absolute — execution happens inside a worktree, not the original repo directory
    - Be conservative: if unsure whether two sections conflict, keep them sequential
    - Read actual source files to verify dependencies — don't guess from section names alone
    - A preparation step is only worth it when it unlocks 3+ parallel sections
    - The contract does NOT change what scenarios exist — only execution order and grouping
    - Never skip the three-independence check, even when it's obviously simple — state the result
    - Sections that share functions within the same file MUST be in the same work unit as SEQUENTIAL
    - For greenfield: prefer per-section files over monolithic files when it enables parallelism
  """
)
```

## After Design: Update the Driver

The execution contract must be written into the driver skill's `## Execution Contract` section, **replacing** any previous contract. There must be exactly one contract at any time.

The File Targets section in the contract is the authoritative source for which files each section modifies. The driver passes these targets to each worker in the dispatch prompt.

## Replanning

If the driver needs to deviate from the contract during execution (e.g., a batch fails and the dependency graph changes), it must:
1. Stop execution
2. Dispatch a new execution design subagent for the remaining work
3. Replace the old contract with the new one
4. Resume execution under the new contract

## When to Go Shallow

This step is always performed, but depth scales with phase complexity:

- **3 or fewer sections, no shared files**: use the same EXACT format but with a single batch
- **Phase with clear prep opportunity** (e.g., signature migration): full prep-gated design
- **Phase with many independent sections**: full parallel batching plan
- **User explicitly asks to skip**: fall back to sequential execution
