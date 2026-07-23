---
name: execute-plan
description: "Executes an approved implementation plan autonomously. Reads plan.md, works through tasks sequentially, runs verifications, commits on success, and stops on failure. Human reviews the PR, not each task. Resumes from checkboxes if interrupted. Trigger on \"execute plan\", \"run the plan\", \"execute <slug>\", \"execute <slug>-plan.md\", or as the natural next step after write-plan when the user approves execution."
---

# Execute Plan — Build It

Executes an approved implementation plan produced by [write-plan](write-plan.md). The plan
contains self-contained tasks with exact code, verification commands, and commit
instructions.

**This is an agentic workflow.** Read file state, execute autonomously, update
state, loop until a gate (failure or completion). Do not ask the human per task.

**The plan is the contract.** Execute literally. Do not improvise, refactor, or
auto-fix failures.

**Announce at start:** "I'm executing the plan. I'll work through tasks
autonomously and stop if any verification fails. You'll review the PR at the
end."


## Phase 0 — Load and Parse State

Parse the source the same way [write-plan](write-plan.md) resolves plans:

| Input | Resolution |
|-------|------------|
| **File path** — ends in `.md` or contains `/` | Read directly. Resolve relative paths from cwd. |
| **Slug** — kebab-case (e.g. `auth-refactor`) | Read `$ARTIFACT_DIR/<scope>/<slug>/<slug>-plan.md` (resolve `<scope>` per the artifact-dir rule) |
| **Omitted** | List recent `*-plan.md` files under `$ARTIFACT_DIR/` (walk up to three levels deep to cover `<customer>/<workspace>/<slug>/`, plain `<scope>/<slug>/`, and flat `<slug>/` layouts; last 7 days) and ask which to run |

**After loading:**

1. Derive `<slug>` from the filename or directory.
2. Parse every `### Task N:` section.
3. For each task, determine status from its step checkboxes:
   - **Done** — all `- [x]` checkboxes in the task section
   - **Pending** — any `- [ ]` checkbox remains
4. Identify `current_task` = first pending task by number.
5. Report state (do not ask what to do next):

> Plan: `<slug>-plan.md`
> Tasks: N total, M complete, R remaining
> Starting from Task K: [title]

If all tasks are complete, skip to **Phase 3 — Completion**.

### Approval gate

Before executing pending tasks, confirm the plan was approved:

- If the plan or user explicitly says it is approved: continue.
- If this is a fresh plan with zero completed tasks and no approval signal: ask once:
  > "This plan hasn't been marked approved. Has it been reviewed? I'll execute literally and stop on any failure."

Do not block resume when M > 0 (execution already in progress).


## Phase 1 — Pre-flight

Run these checks autonomously. Only stop when a check fails.

### 1. Working directory

Confirm cwd is the target application repo (not a notes vault or artifact
directory). If ambiguous, ask once which repo to use.

### 2. Branch check

```bash
git branch --show-current
```

- If on `main` or `master`: create and switch to a feature branch:
  ```bash
  git checkout -b feat/<slug>
  ```
- If already on a feature branch: continue.

Use existing branch naming from repo rules when present (e.g. `feat/<slug>`,
`<TICKET-ID>/<slug>`). Do not rename an in-progress branch.

### 3. Clean working tree

```bash
git status --porcelain
```

- If clean: continue.
- If dirty: **STOP** — report uncommitted files. Do not stash or commit unless
  the user explicitly asks in this session.

### 4. Dependencies (optional)

If `package.json`, `pnpm-lock.yaml`, or `package-lock.json` changed since the
last completed task commit, run the project's install command (`pnpm install`,
`npm install`, etc.). Otherwise skip.

### 5. Execution mode

If not specified by the user, choose once at start:

| Mode | When |
|------|------|
| **Inline** (default) | ≤10 pending tasks, or user says "inline" |
| **Subagent per task** | >10 pending tasks, or user says "subagent" / "isolated" |

Report the chosen mode in the opening announcement.


## Phase 2 — Execute Tasks

For each pending task, in numeric order:

### Step 1 — Announce

> Executing Task N/M: [short description from heading]

### Step 2 — Execute steps literally

For each `- [ ]` step in the task:

1. **Create / modify files** — use the exact paths and complete code from the
   plan. Do not paraphrase, "improve", or skip steps.
2. **Run commands** — execute shell commands as written.
3. Do not reference "similar to Task X" — each task must stand alone.

After completing a step's actions, mark that step `- [x]` in the plan file.

### Step 3 — Verify

Run the verification command from the task exactly as written.

**On success:**

1. Run the commit command from the task (or compose one matching the plan's
   intent if the plan uses a template).
2. Mark all task checkboxes `- [x]`.
3. Brief progress line: `Task N/M complete.`
4. Continue to the next pending task.

**On failure — STOP GATE:**

> Task N failed verification.
>
> Command: `[exact command]`
>
> Error:
> ```
> [relevant output]
> ```
>
> Plan paused at Task N. I won't auto-fix or continue. Revise the plan or fix
> the blocker, then re-run `execute plan`.

**STOP.** Do not continue to later tasks.

### Inline vs subagent execution

**Inline (default):** Execute Step 2–3 in the current session.

**Subagent per task:** For each task, spawn a task-executor agent:

```
description: "Execute Task N: [short title]"
subagent_type: "task-executor"
run_in_background: false
prompt: |
  ## Task
  [paste full task section including Files, steps, verification, commit]
```

- If response contains `FAILED:` → STOP GATE (same as verification failure).
- If `SUCCESS` → mark task complete in plan file, continue.


## Phase 3 — Completion

When every task section has all checkboxes checked:

### 1. Final verification

Run each item under the plan's **Verification Summary** section (if present).
If the section is missing, run the repo's standard gates when known:
`pnpm lint`, `pnpm test`, `pnpm typecheck` (or project equivalents).

### 2. Push and open PR

If final verification passes, delegate to the `github-pr-description` skill for
branch push and PR creation. Provide it with:

- Summary from the plan **Goal**
- Checklist of completed tasks
- Verification steps and automated test commands run
- Ticket number if one exists in the plan or spec

Do not create the PR inline with `gh pr create` — always go through
`github-pr-description` so description format, ticket linking, and impact
assessment stay consistent.

### 3. Report completion

> Plan complete.
>
> - N/N tasks executed
> - Final verification passed
> - PR: [link]
>
> Ready for your review.

If the user forbids push/PR in this session, report branch name and verification
results instead.


## Failure Handling

| Failure | Action |
|---------|--------|
| Verification fails | STOP, report command + output, wait |
| Git commit fails | STOP, report error (conflict, hook failure) |
| File path missing | STOP — plan may be stale or wrong repo |
| Plan references undefined symbol | STOP — plan internal inconsistency |
| Command timeout (>5 min) | STOP — report; do not retry blindly |
| Subagent FAILED | STOP — same as verification failure |

**Principle: STOP, don't fix.** The plan was approved as-is. Improvised fixes
cause drift between plan and PR.


## Resumability

State lives in two places:

1. **Plan file checkboxes** — which tasks/steps are done
2. **Git commits** — code changes for completed tasks

Re-running `execute plan <slug>`:

1. Re-reads the plan
2. Skips tasks already checked
3. Resumes from the first pending task

No separate "resume" command. Do not reset checkboxes unless the user asks.

If git history and checkboxes disagree (e.g. commit exists but box unchecked),
trust git for code state and align checkboxes to match reality after confirming
with `git log`.


## Integration

```
incept → spec.md
tech-incept → design.md
write-plan → plan.md   ← human approves
execute-plan → commits + github-pr-description → PR   ← human reviews PR
```

Plans live at:
`$ARTIFACT_DIR/<scope>/<slug>/<slug>-plan.md`

Resolve `$ARTIFACT_DIR` and `<scope>` per the artifact-dir rule.


## Key Principles

- **Agentic, not chatty** — read state, loop, update state; gates only on failure or PR
- **Literal execution** — the plan has complete code for a reason
- **Human gate at PR** — not per task
- **Files are state** — checkboxes enable resume across sessions
- **Ask before git push/merge** — per user and repo git workflow rules
