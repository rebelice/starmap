# Starmap As Coverage Planning Plus Proof-Preserving Parallelization

This document records the current design direction discussed for evolving `starmap`. It is intentionally a methodology note, not a concrete prompt spec or implementation mechanism.

## Goal

Reframe `starmap` from a scenario-charting tool into a higher-level planning system that can support parallel execution without reducing coverage observability or correctness confidence.

Target definition:

- coverage planning
- execution architecture design
- proof-preserving parallelization system

## Why The Current Model Is Not Enough

The current `starmap` framing is strong at scenario decomposition, but weaker at execution design. It can split a large goal into sections and phases, yet that does not guarantee the sections are safe to run in parallel.

The main failure mode is treating topic-level separation as if it were execution-level separation. Two sections may be semantically different while still colliding on:

- shared caller files,
- shared dispatch layers,
- shared test assets,
- shared progress-tracking documents,
- shared integration proof surfaces.

This leads to a familiar pattern:

- planning says the sections are independent,
- workers still edit the same hotspots,
- local verification becomes partial or misleading,
- correctness is deferred to late integration,
- the batch still finishes, but with extra friction and less trustworthy intermediate signals.

## New Starmap Definition

The new model should treat `starmap` as three things at once.

### 1. Coverage Planning

This remains the foundation. `starmap` still needs to enumerate the scenario space, define sections, and make progress measurable in concrete pass/fail terms.

### 2. Execution Architecture Design

`starmap` should no longer stop at "what sections exist." It should also decide how those sections should be executed:

- sequentially,
- directly in parallel,
- only after prep,
- only with a later integration pass.

### 3. Proof-Preserving Parallelization

Parallel execution should be treated as a constrained optimization, not a default behavior. The system should preserve:

- coverage visibility,
- correctness proof strength,
- integration clarity,
- auditability of progress.

## Three Kinds Of Independence

Future `starmap` planning should distinguish three different kinds of independence.

### Semantic Independence

Two sections belong to different features or conceptual areas.

This is necessary, but it is the weakest form of independence.

### Change-Surface Independence

Two sections do not need to modify the same shared files, shared callers, shared registries, or shared progress artifacts.

This is the key requirement for safe parallel execution.

### Proof Independence

A section can complete with a trustworthy verification result that is not invalidated by other in-flight sections.

This determines whether intermediate completion signals still mean anything.

Direct parallel execution should only be considered safe when all three forms of independence hold.

## Core Planning Shift

The central shift is from work decomposition to change-surface decomposition.

Old question:

- what feature group does this section belong to?

New question:

- what files, proof surfaces, and integration boundaries does this section actually touch?

This means `starmap` should eventually reason about:

- owned targets,
- shared surfaces,
- verification scope,
- integration dependencies,
- progress-writing responsibility.

This document does not define the exact metadata format yet. It only establishes that these dimensions are necessary.

## Preferred Execution Shape

The emerging execution shape is a staged model rather than immediate free-form parallelism.

### 1. Prep

Handle shared surfaces up front.

Typical examples:

- introducing compatibility shims,
- updating shared callers once,
- establishing common test scaffolding,
- deciding who owns progress updates.

### 2. Parallel Implementation

Workers execute only the implementation surfaces that are truly isolated.

At this stage, workers should avoid writing shared source-of-truth artifacts and avoid opportunistic edits outside their owned change surface.

### 3. Integrate And Verify

A dedicated integration step merges the batch, updates shared progress artifacts, and produces the batch-level proof.

This is where full build and canonical test verification belongs.

## Coverage Preservation Principles

Parallelization should not weaken coverage tracking.

The strongest principle discussed so far is single-writer authority for progress:

- workers report structured coverage deltas,
- driver or integration logic updates the canonical scenario ledger,
- shared progress files should not be concurrently edited by many workers.

This keeps progress observable, auditable, and replayable.

## Correctness Preservation Principles

Parallelization should not remove proof obligations. It should only restructure them.

The intended proof stack is layered:

### Section-Local Proof

Each worker proves its own local invariants and section-specific results.

### Batch Integration Proof

The integration step proves that the batch is coherent after merge.

### Global Proof

At phase or milestone boundaries, the system proves the broader repo or subsystem still satisfies the canonical build and test requirements.

This model does not weaken correctness. It redistributes proof responsibility more explicitly.

## What The Overall Starmap Flow Becomes

Under this direction, the high-level `starmap` flow changes from pure scenario planning to architecture-aware planning.

### Previous Shape

1. understand the goal
2. explore the reference and local implementation
3. chart scenarios
4. group them into phases and sections
5. generate worker and driver skills
6. execute

### Intended Shape

1. understand the goal
2. explore the feature terrain
3. explore the change terrain
4. chart scenarios
5. annotate section-level change surfaces and proof boundaries
6. design the execution architecture
7. decide which work is sequential, prep-gated, parallelizable, or integration-only
8. generate execution guidance
9. execute with staged verification

The important change is that `starmap` becomes responsible not only for "what to cover" but also for "how to execute without invalidating the proof story."

## High-Level Starmap Structure

Under this direction, `starmap` should be understood as a planning system with four layers.

### 1. Goal Layer

This layer defines:

- what outcome must be matched or implemented,
- what reference behavior matters,
- what the canonical success criteria are,
- what the final proof of completion will be.

This is where the planning process decides what "done" means at the highest level.

### 2. Scenario Layer

This layer defines the coverage map:

- scenario inventory,
- section boundaries,
- phase boundaries,
- pass/fail checkpoints,
- explicit coverage scope.

This remains the main coverage-planning function of `starmap`.

### 3. Change-Surface Layer

This layer translates scenario sections into execution-relevant boundaries:

- owned implementation surfaces,
- shared surfaces,
- likely integration points,
- verification boundaries,
- proof-sensitive hotspots.

This is the layer that determines whether a phase is actually parallelizable or only appears parallelizable at the topic level.

### 4. Execution-Architecture Layer

This layer decides how execution should be staged:

- what must run sequentially,
- what requires prep,
- what may run in parallel,
- what requires integration,
- where proof checkpoints belong.

This is the new layer that turns `starmap` from a scenario map into an execution-design system.

## Inputs

The evolved `starmap` should eventually reason over a consistent set of planning inputs.

### Goal Inputs

- target task or compatibility goal,
- expected reference behavior,
- local subsystem or code area in scope,
- completion criteria.

### Coverage Inputs

- scenario source documents,
- reference docs or implementation behavior,
- prior scenario maps,
- existing pass/fail ledgers.

### Change Inputs

- current code structure,
- shared entrypoints and shared callers,
- shared test surfaces,
- shared progress artifacts,
- known historical conflict areas from prior phases or batches.

### Proof Inputs

- required local checks,
- required integration checks,
- required final or milestone checks,
- any constraints on what evidence counts as completion.

## Outputs

The new `starmap` should produce more than a scenario chart.

### 1. Coverage Output

A durable scenario map with explicit sections and phases.

### 2. Execution Output

A high-level execution architecture that states:

- which phases are sequential,
- which phases are prep-gated,
- which sections are directly parallelizable,
- which work must be integrated centrally.

### 3. Proof Output

A proof structure that assigns responsibility for:

- section-local proof,
- batch integration proof,
- phase-level or global proof.

### 4. Risk Output

A planning view of where parallelization is likely to distort:

- coverage observability,
- local verification trustworthiness,
- integration stability,
- total execution predictability.

## Stage Responsibilities

The planning stages should carry clear responsibility boundaries.

### Understand Goal

Responsibility:

- define the target outcome,
- define the canonical reference,
- define the final success proof.

Failure if skipped:

- later sections may optimize for the wrong completion condition.

### Explore Feature Terrain

Responsibility:

- map the feature and behavior space,
- identify variants and edge cases,
- establish the coverage surface.

Failure if skipped:

- scenario coverage will be incomplete or poorly shaped.

### Explore Change Terrain

Responsibility:

- identify shared callers,
- identify shared dispatch and registries,
- identify shared tests and shared progress artifacts,
- identify likely integration hotspots.

Failure if skipped:

- parallelization decisions will rely on topic intuition instead of execution reality.

### Chart Scenarios

Responsibility:

- produce the scenario ledger,
- organize sections and phases,
- make coverage measurable.

Failure if skipped:

- progress cannot be tracked or audited cleanly.

### Annotate Change Surfaces And Proof Boundaries

Responsibility:

- connect each section to its execution footprint,
- identify proof-sensitive sections,
- identify integration-dependent sections.

Failure if skipped:

- sections may look independent while still colliding at execution time.

### Design Execution Architecture

Responsibility:

- choose sequential vs prep-gated vs parallel vs integration-only execution,
- place proof checkpoints,
- preserve coverage and correctness during execution.

Failure if skipped:

- execution becomes ad hoc and correctness gets reconstructed too late.

### Generate Execution Guidance

Responsibility:

- turn the architecture into instructions for driver and worker behavior,
- encode role boundaries without collapsing into low-level mechanism yet.

Failure if skipped:

- execution will drift away from the planning assumptions.

## Responsibility Boundary Of Starmap

Even in the expanded model, `starmap` should still stop at the architecture boundary.

It should decide:

- what must be covered,
- what the execution shape should be,
- where proof obligations live,
- where parallelization is appropriate or unsafe.

It should not, at this stage, be required to decide:

- the exact transport or workspace mechanism for workers,
- the exact branch or worktree model,
- the exact merge protocol,
- the exact automation implementation details.

Those belong to later execution-system design.

This boundary is important because it keeps `starmap` focused on planning correctness, not orchestration mechanics.

## Time Tradeoff

This design does introduce more upfront planning work, especially when exploring change terrain.

That added cost is acceptable only when it offsets downstream execution noise. The expected tradeoff is:

- more explicit planning time before parallelization,
- less hidden conflict cost during worker execution,
- fewer misleading partial-verification states,
- lower integration uncertainty at the end of a batch.

This should not become a mandatory heavyweight process for every phase. The extra planning depth is most justified when:

- a phase is large,
- parallel execution is under consideration,
- shared callers or dispatch layers are likely,
- multiple sections depend on the same proof surfaces,
- prior batches have shown integration friction.

For small or obviously isolated work, the heavier architecture pass may not be worth it.

## Default Planning Mode

The current decision is to use a heavy `starmap` frame by default, while allowing aggressive pruning inside that frame.

This means the system should not branch early into separate "light" and "heavy" planning modes. Instead, every task should begin with the same high-level planning questions:

- what must be covered,
- what change surfaces matter,
- what proof obligations exist,
- what execution shape is appropriate.

After those questions are asked, the planner may conclude that some dimensions do not require further expansion for the current phase.

### Why Not Maintain Separate Light And Heavy Modes

Maintaining two planning modes looks cheaper at first, but it makes the most important decision happen too early: whether a task is simple enough to skip deeper execution and proof analysis.

That creates a structural risk:

- tasks that look simple may still hide shared surfaces,
- tasks marked "light" may skip the exact checks that would have revealed execution risk,
- planning quality becomes more variable across phases and operators.

The result may be faster average startup, but less reliable final outcomes.

### Why Heavy Plus Pruning Is Preferred

A heavy-by-default frame preserves a single planning language and a single quality bar. It ensures that change-surface and proof questions are never forgotten entirely.

Pruning then controls cost:

- sections that are obviously isolated do not need deep change-surface expansion,
- phases that are clearly sequential do not need elaborate parallel execution design,
- straightforward proof stories do not need complex proof layering.

This keeps the framework uniform while allowing shallow execution paths when the task genuinely warrants it.

### Practical Interpretation

In practice, this means:

- one planning model,
- one set of top-level questions,
- variable depth of analysis,
- no separate lightweight methodology.

The distinction is therefore not between two different `starmap` systems. The distinction is between:

- fully expanded planning, and
- quickly pruned planning

inside the same system.

## Pruning Boundary

Pruning should reduce planning depth, but it should not remove the core checks themselves.

Acceptable pruning:

- documenting that a phase is sequential and stopping there,
- recording that change surfaces are clearly isolated without full hotspot expansion,
- recording that batch-level integration proof is unnecessary because no batch exists.

Unacceptable pruning:

- skipping change-surface thinking entirely,
- assuming topic separation implies execution separation,
- omitting proof ownership,
- leaving progress ownership ambiguous.

This keeps pruning honest. It is a reduction in elaboration, not a return to intuition-driven planning.

## Design Boundary For Now

This note intentionally stops short of defining:

- exact metadata schemas,
- exact prompt wording,
- exact driver or worker protocols,
- exact batching heuristics,
- exact automation for conflict detection.

Those belong to a later mechanism-design step.

## Summary

The current direction is to evolve `starmap` into a system that jointly plans:

- what must be covered,
- what change surfaces are involved,
- what proof obligations exist,
- what execution architecture preserves both speed and trust.

In short, `starmap` should become a coverage planning plus execution architecture design plus proof-preserving parallelization system.
