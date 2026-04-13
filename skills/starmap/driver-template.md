# Driver Skill Template

Generate a driver skill at `~/.claude/skills/<project>-driver/SKILL.md` using this template. The driver manages progress, dispatches worker subagents, and performs integration edits (merging test files, updating SCENARIOS checkboxes). It never does section implementation.

~~~markdown
---
name: <project>-driver
description: Use when driving the <project> scenario coverage effort. Manages progress,
  dispatches worker subagents, tracks overall completion.
---

# <Project> Driver

## Usage

/<project>-driver <command>

## Commands

- **status** — Show progress per section. Read SCENARIOS-<project>.md with the Read tool and count checkboxes (`- [x]` = pass, `- [~]` = partial, `- [ ]` = pending) per section. Do NOT use shell commands (awk/gawk/sed) to parse — use the Read tool and count in your response.
- **next** — Dispatch next pending section as a fresh subagent
- **run <section>** — Dispatch specific section as a fresh subagent
- **run-all** — Run all remaining pending sections (auto-pilot). Follows the execution contract if one exists, otherwise sequential.
- **plan** — Show recommended execution order
- **report** — Full progress report. Same approach as `status` — read the file, count checkboxes, summarize.

## Subagent Dispatch

The `next` and `run` commands dispatch each section as a fresh subagent. Use your platform's subagent mechanism (e.g., Agent tool in Claude Code). Example prompt:

Agent(
  description: "Execute section X.Y",
  prompt: """
    You are a <project> worker. Execute section X.Y of the starmap.

    ## Instructions
    Read the worker skill at <worker-skill-path> and follow its process exactly.

    ## Task
    Section to execute: X.Y
    SCENARIOS-<project>.md location: <path>
    Project directory: <path>

    ## File Targets (from execution contract)
    Target files for this section: <list from contract's File Targets section>
    Proof command: <from contract's Proof section>

    ## Existing Infrastructure
    Before writing any test code, read the existing test files to understand:
    - Test harness and helpers
    - How existing tests are structured (naming, patterns, imports)
    - Which test files exist and what sections they cover

    Key files to read first:
    - <test-infrastructure-file>
    - <existing-test-file>

    ## Re-entry Handling
    If a test function for this section already exists (from a prior partial run),
    do NOT create a duplicate. Instead:
    - Read the existing test function
    - Identify which test cases are already present
    - Only add NEW test cases for scenarios still marked [ ] in SCENARIOS-<project>.md
    - If all pending scenarios are already covered, skip to running tests

    ## Return Format
    After completing all steps (including commit), return a summary:
    - Section name
    - Scenarios passed: N/M
    - Fixes applied: <list>
    - Partial/skipped: <list with reasons>
    - Files modified: <list of all files you changed>
    - Out-of-Targets files: <files modified that were NOT in the dispatch targets, or "none">
    - Proof result: pass/fail (did section-local proof pass?)
    - Commit SHA: <from git log --oneline -1>
    - Checkbox updates: <which scenarios to mark [x] or [~]>

    All file paths must be relative to the worktree root (when in worktree) or project root (when sequential).
  """
)

## run-all Command

Runs all remaining pending sections following the execution contract:
1. **Create project worktree**: create a dedicated worktree for this starmap project (`git worktree add`). All execution happens inside this worktree — this isolates the project from other concurrent starmap projects in the same repo.
2. Identify all sections with [ ] pending
3. Read the execution contract (the `## Execution Contract` section in this skill file). If no contract exists, run sections sequentially in section-number order.
3a. **Record pre-phase SHA** at the start of each phase: capture `git rev-parse HEAD` and store it as `<pre-phase-sha>` for that phase's Step 6b Codex phase review.
4. **Pre-dispatch consistency check**: before dispatching each batch, verify:
   - The work units in this batch match the contract exactly
   - Sections marked as SEQUENTIAL within a unit are dispatched to a single worker (not split)
   - No unit is dispatched that the contract says belongs to a later batch
   - Proof commands in the contract match the dispatch prompts being sent to workers
   If any inconsistency is found, stop and replan — do not override the contract.
5. For each batch per the contract:
   a. **Record pre-batch SHA**: before dispatching, capture the current HEAD of the project worktree branch (`git rev-parse HEAD`). Store it as `<pre-batch-sha>` for Step 5e.
   b. Dispatch subagent(s):
      - **Sequential** (batch size = 1): dispatch single subagent without worktree isolation
      - **Parallel** (batch size > 1): dispatch all subagents simultaneously, each with `isolation: "worktree"`. Worktree is required for parallel execution because workers in the same directory break the build.
   c. **Verify worktree results** (parallel only): for each worker, check that the return includes a commit SHA. If missing (worktree cleaned up), the worker failed to commit — retry immediately.
   d. **Merge worktree branches** (parallel only): squash-merge each worker's branch into the current project worktree branch one at a time (`git merge --squash <branch> && git commit`). This keeps git history linear. After each merge, run a quick build check. If merge conflicts occur, classify and handle:
      - **Caller update conflict** (two versions of the same call site — e.g., one with error handling, one without): take the more complete version
      - **Additive conflict** (both branches added code at the same insertion point): keep both additions, fix ordering if needed
      - **Structural conflict** (incompatible changes to the same function body): stop and replan — the contract missed a dependency
      After all branches merged, merge per-section test files into the canonical test file, remove per-section files, and commit.
   e. **Batch integration proof** (parallel only): run the batch integration proof command. If it fails, identify which section caused the regression.
   f. **Mandatory Codex review** (every batch — parallel AND sequential): after Step 5e proof passes, run a Codex adversarial review on the landed diff. This is not optional and cannot be skipped.
      - **Launch**: invoke `/codex:review --base <pre-batch-sha> --background` immediately after batch integration proof passes. Background mode lets the driver continue setting up the next batch while Codex reviews.
      - **Gate**: before dispatching the NEXT batch (Step 5a of the next iteration), call `/codex:status` and block until the launched review completes. If the next batch is ready before Codex finishes, wait — do not dispatch.
      - **Interpret result**:
        - `approve` → mark affected scenarios [x], proceed to next batch
        - `needs-attention` → **auto-fix first, then defer**. Do NOT stop execution. Increment a per-batch `codex_attempt` counter (starts at 1; the first review is attempt 1).
          - **Attempt 1 or 2**: dispatch a fix worker targeted at the findings (see "Codex Fix Worker Dispatch" below). When the fix worker returns, re-run Step 5e (batch integration proof) and Step 5f (Codex review with a new `<pre-batch-sha>` = HEAD before the fix worker, so the review covers just the fix). If the fix worker's own commit makes the review pass, mark scenarios [x] and proceed to the next batch.
          - **Attempt 3 (after 2 failed fix attempts on the same batch)**: **defer, do not stop**. Append a full entry to the driver's `## Deferred Codex Findings` section (see format below), mark the affected scenarios [~] with suffix `(codex-deferred: batch-<id>)`, and CONTINUE to the next batch. The fix worker's last commit stays in the tree — its build/test passed even though Codex still objected. Downstream batches run against this state, same as any other commit.
      - **Rationale**: batch integration proof catches build/test failures; Codex review catches the failure modes that build/test cannot — cross-section semantic conflicts, missed invariants, test quality gaps, and stale assumptions between parallel workers. Most findings are the kind a fix worker can resolve autonomously (missing test case, missed guard, stale assumption); the 2-attempt auto-loop handles that majority. Findings that persist are deferred to the end-of-run report so `run-all` stays uninterrupted — overnight runs finish overnight, and all decisions pile up at the end where the user can triage them together with full context.
   g. **Check out-of-Targets**: if any worker reports files modified outside its declared targets, note this — the execution contract's File Targets may need updating via replan.
   h. Print section summary, then continue
6. **Phase-end gates** (all mandatory, run in order — no skipping):
   a. **Global proof**: run the global proof command (canonical build + full test suite). Must pass before moving on.
   b. **Mandatory Codex phase review**: run `/codex:review --base <pre-phase-sha> --wait` against the full phase diff (pre-phase-sha = HEAD at the start of the phase, captured at Step 3a). Use `--wait` here because phase end is already a hard stop — there is no parallel work to overlap. Same auto-fix-first-then-defer loop as batch review:
      - `approve` → phase complete, move to next phase
      - `needs-attention` on attempt 1 or 2 → dispatch a fix worker targeted at the findings, re-run global proof (Step 6a) + Codex phase review (Step 6b). The `<pre-phase-sha>` stays the same across retries so the review scope remains the full phase.
      - `needs-attention` after 2 failed attempts → **defer, do not stop**. Append entry to `## Deferred Codex Findings` (scope: phase-level), do NOT mark the phase's passing scenarios as failed (they already passed batch review earlier), but DO record the phase-level finding separately. Continue to the next phase.
7. Stop on fatal failure only when the build is broken or a worker cannot recover. Codex `needs-attention` after 2 auto-fix attempts does NOT stop the run — the findings are deferred and execution continues. Partial ([~]) scenarios also continue.
8. Print cumulative progress summary after every 10 sections, but keep going — do not pause or ask for confirmation. Codex auto-fix loops and defers are transparent to this flow; the run reaches completion regardless.
9. Resumable: re-running picks up where it left off (checkboxes are durable; `## Deferred Codex Findings` is also durable across sessions)
10. If a phase has 0 pending sections, skip to phase-end gates (global proof + Codex phase review) for that phase, then move to the next phase
11. **Merge project worktree back**: when all phases complete, squash-merge the project worktree branch back to the original branch and clean up the worktree.
12. **End-of-run triage**: after the merge-back, read the driver's `## Deferred Codex Findings` section. If non-empty, print a consolidated report:
    - Total deferred entries count (batch-level and phase-level)
    - For each entry: scope (batch-id or phase-id), affected scenarios, all findings from all attempts (verbatim), diffs from each fix worker's attempt, current state of the affected files
    - Present the three triage options to the user, per entry (or grouped if findings are related):
      (i) **Reopen** — dispatch one more manual fix worker with additional user-provided guidance
      (ii) **Replan** — run a fresh execution design subagent for the affected scope, replace the contract, re-execute
      (iii) **Override** — accept the finding as a false positive or acceptable risk, mark the affected scenarios [x] with a suffix `(codex-override: <user justification>)`, record the justification in the driver's `## Codex Overrides` log
    After the user decides each, clear the corresponding entry from `## Deferred Codex Findings`. The starmap is complete when that section is empty.

## Codex Fix Worker Dispatch

When a Codex review returns `needs-attention` and the `codex_attempt` counter is below 3, dispatch a targeted fix worker. The fix worker is NOT a regular section worker — it reads findings and produces a minimal patch.

Agent(
  description: "Codex fix attempt <N> for batch <batch-id>",
  prompt: """
    You are a Codex fix worker for the <project> starmap. A Codex adversarial
    review flagged the following findings on the batch/phase just landed. Your
    only job is to resolve these findings with the smallest possible patch.

    ## Findings (verbatim from Codex)
    <paste every finding: file, line_start, line_end, confidence, recommendation, body>

    ## Scope
    Review scope: <pre-batch-sha> or <pre-phase-sha> .. HEAD
    Project worktree: <path>
    Attempt number: <N> of 2

    ## Instructions
    1. Read each finding and the cited file:line locations in full.
    2. For each finding, decide: is it a real bug, a missing test case, a
       missing guard, or a Codex false positive?
       - Real bug / missing guard → fix the production code.
       - Missing test case → add the test case that would have caught this.
       - Stale assumption between workers → reconcile the affected files.
       - False positive → document in the commit message why, and skip the fix
         (but only if you can explain it; "looks fine to me" is not enough).
    3. Run the batch/phase proof command to verify your fix doesn't break
       anything that was previously green.
    4. Commit all changes in ONE commit with message:
       "codex-fix(<batch-id>): attempt <N> — <short summary of findings addressed>"
    5. Return a summary listing which findings you addressed, which you deemed
       false positive (with reasons), and the commit SHA.

    You MUST NOT:
    - Add new features or scope beyond the findings
    - Refactor unrelated code
    - Modify SCENARIOS-<project>.md checkboxes (driver's job)
    - Skip the proof command
  """
)

The driver captures the fix worker's commit, then re-runs the proof + Codex review using the fix worker's pre-fix HEAD as the new `--base`. This scopes the second Codex pass to just the fix, keeping the review signal tight.

## Deferred Codex Findings

When a batch or phase review still returns `needs-attention` after 2 auto-fix attempts, the driver appends an entry to the `## Deferred Codex Findings` section of its own skill file (this section; it's part of the durable driver state). Format:

```markdown
### Entry <N>: <scope> (<batch-id or phase-id>)

- **Deferred at**: <ISO timestamp>
- **Scope type**: batch | phase
- **Affected sections**: <list of section IDs>
- **Affected scenarios**: <list, with their SCENARIOS line numbers>
- **Original Codex findings (attempt 1)**:
  - file: <path>, lines: <L1-L2>, confidence: <0..1>
    recommendation: <verbatim>
    body: <verbatim>
  - ... (one block per finding)
- **Fix attempt 1**: commit <sha>, summary: <what the fix worker addressed / deemed false positive>
- **Codex findings (attempt 2)**:
  - ... (same format)
- **Fix attempt 2**: commit <sha>, summary: <...>
- **Codex findings (attempt 3, final)**:
  - ... (same format)
- **Current state**: affected scenarios marked [~] with `(codex-deferred: <id>)` suffix; fix attempt 2's commit is in the tree

### Entry <N+1>: ...
```

The `status` and `report` commands surface the deferred-findings count alongside normal progress stats. `next` and `run-all` skip scenarios marked with the `(codex-deferred: ...)` suffix — they are handled exclusively by Step 12 end-of-run triage.

## Codex Overrides

When the user chooses option (iii) override during end-of-run triage, the driver appends to a `## Codex Overrides` section of its own skill file. Format:

```markdown
### Override <N>: <scope> (<batch-id or phase-id>)

- **Overridden at**: <ISO timestamp>
- **Affected scenarios**: <list>
- **User justification**: <verbatim from user>
- **Findings overridden**: <brief summary>
```

This makes overrides durable and auditable — anyone reading the driver skill later can see exactly which Codex findings were accepted as risk and why.

## Proof Checkpoints

- **Section-local**: Worker runs its proof command before returning and reports pass/fail. Already implicit (workers run tests), but this is an explicit obligation.
- **Batch integration**: Driver runs integration proof after merging a parallel batch. Sequential sections skip this — section-local proof is sufficient.
- **Codex batch review**: Mandatory after every batch merge (both parallel and sequential), launched in background right after batch integration proof passes, gated before the next batch dispatches. Catches cross-section semantic issues, missed invariants, and test quality gaps that build/test cannot detect. Auto-fix loop: up to 2 fix-worker attempts before escalating to human.
- **Global proof**: Driver runs full proof at phase end. Mandatory — never skip.
- **Codex phase review**: Mandatory after global proof at phase end, run with `--wait`. Second adversarial pass over the full phase diff. A phase is not complete until both global proof and Codex phase review return clean. Same 2-attempt auto-fix loop as batch review.

## Execution Rules

- The execution contract is binding. The driver must not override batch ordering, unit composition, or parallelism decisions. To change the plan, dispatch a new execution design subagent and replace the contract.
- Driver never does section implementation — only dispatches, tracks, and performs integration edits (merging test files, updating SCENARIOS checkboxes, running proof commands)
- Subagent must commit before returning
- The driver is the sole writer of SCENARIOS-<project>.md checkboxes. Workers report results in their return format; driver applies checkbox updates after proof passes AND Codex review returns `approve`. Never mark a scenario [x] on the basis of build/test alone.
- **Codex review is mandatory, not optional.** Every batch merge and every phase-end global proof must be followed by a Codex review. The driver has no flag, config, or override that skips it. If the `/codex:review` command is unavailable in the environment, the driver must stop and report — it does not silently proceed.
- On Codex `needs-attention`: **auto-fix first, then defer**. Dispatch a fix worker, re-run proof + review. Up to 2 auto-fix attempts per batch/phase. If the 3rd attempt still returns `needs-attention`, **defer — do not stop**. Append to `## Deferred Codex Findings`, mark affected scenarios `[~]` with a `(codex-deferred: ...)` suffix, continue to the next batch.
- **run-all never pauses for human input.** There is no mid-run escalation. The only human interaction point in `run-all` is Step 12 end-of-run triage, after every batch and phase has run to completion and the worktree has been merged back.
- Checkbox updates: `[x]` only after `approve` (either first-pass or post-fix-worker). `[~]` with `(codex-deferred: ...)` suffix after defer. Never mark `[x]` based on build/test alone.
- All counts are dynamic — computed from SCENARIOS-<project>.md checkboxes, never hardcoded
- Use the Read tool to parse SCENARIOS-<project>.md — do NOT use shell commands (awk/gawk/sed/python) for markdown parsing
~~~

## Customization Points

When generating the driver skill, replace these with project-specific details:

| Placeholder | Example |
|------------|---------|
| `<project>` | `mysql-catalog` |
| `<worker-skill-path>` | `~/.claude/skills/mysql-catalog-worker/SKILL.md` |
| `<path>` to SCENARIOS-<project>.md | `backend/plugin/catalog/mysql/SCENARIOS-<project>.md` |
| `<test-infrastructure-file>` | `reference_test.go` |
| `<existing-test-file>` | `create_table_reference_test.go` |
| Recommended execution order | Phase 1 first, then Phase 2; section order within each phase per execution design |

## What Stays Where

| Main context (driver) | Subagent (worker) |
|------------------------|-------------------|
| `status` — read checkboxes | Read pending scenarios |
| `plan` — show order | Write tests, fix implementation |
| `next` — pick & dispatch | Run section-local proof |
| `report` — aggregate stats | Commit implementation + tests |
| Update checkboxes, merge branches | Report results (never writes SCENARIOS) |
| Capture pre-batch / pre-phase SHAs | — |
| Launch + gate mandatory Codex review | — |
| Dispatch fix worker on `needs-attention` | Fix worker handles findings (different prompt than section worker) |
| Append to `## Deferred Codex Findings` on 3rd fail | — |
| End-of-run triage (Step 12): present deferred findings | — |
