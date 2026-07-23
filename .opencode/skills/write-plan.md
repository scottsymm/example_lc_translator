---
name: write-plan
description: "Convert approved design into micro-tasks with exact code touchpoints and concrete verification steps."
---

# Write Plan — Design to Tasks

Execution planning skill. Breaks an engineering design into ordered micro-tasks.

**Output:** `<slug>-plan.md` → `$ARTIFACT_DIR/<scope>/<slug>/`


# write-plan

Generates a detailed, micro-task implementation plan from an approved design or
requirements source. Every task is small enough to execute in one action, with
exact file paths, complete code, and a verification step.

**The plan is written for an executor with zero codebase context and no
judgment.** This means: no "implement X here", no "similar to Task N", no
placeholders. Every task is self-contained.

**Announce at start:** "I'm using write-plan to create the implementation plan."


## Phase 0 — Locate the Source

The user invokes with `write plan` or `write plan <source>`. Parse `<source>`
the same way `tech-incept` does:

| Source format | How to resolve |
|---|---|
| **Design from tech-incept** — no source given, `<slug>-design.md` exists at the current slug path | Read `$ARTIFACT_DIR/<scope>/<slug>/<slug>-design.md`. This is the golden path. |
| **File path** — ends in `.md` or contains `/` | Read the file directly. Resolve relative paths from cwd. |
| **Linear ticket** — matches `ENG-123`, `PROJ-42`, etc. | Fetch via `linear` MCP tools. Extract title, description, acceptance criteria. |
| **Idea name** — plain words, no extension | Derive kebab-case slug → look for `<slug>-design.md` first, then `<slug>-spec.md` at `$ARTIFACT_DIR/<scope>/<slug>/`. |
| **`for <customer>` phrase** | Parse `<customer>` per the artifact-dir rule and apply when resolving paths. |
| **Omitted** | Ask: "What should I plan? Give me a design/spec path, ticket ID, or idea name." |

**After resolving:**

1. Read the source silently.
2. If source is a `spec.md` with no `<slug>-design.md`, flag it: "This spec hasn't been
   through technical design yet. Want me to run `tech-incept` first, or plan
   directly from the spec?"
3. Derive `<slug>` for the output path (same rules as `tech-incept`).


## Phase 1 — Scaffold

1. Using the `<slug>` derived in Phase 0, resolve `$ARTIFACT_DIR` and `<scope>`
   (see artifact-dir rule; parse `for <customer>` from the invocation if present).
2. Create directory: `$ARTIFACT_DIR/<scope>/<slug>/`
3. If `$ARTIFACT_DIR/<scope>/<slug>/<slug>-inception.md` does not exist, write it
   from the template below — **do not pre-fill Idea or Goal**; keep Phase 1 minimal.
4. Open in editor/vault if integration is configured (skip if file already existed).
5. Confirm: `Inception file created: $ARTIFACT_DIR/<scope>/<slug>/<slug>-inception.md`
   (or `Inception file exists: …` if already present — no update)

**`<slug>-inception.md` template:**

```markdown
title: <Idea Name>
tags:
  - inception
  - <slug>
keywords: []
incepted: YYYY-MM-DD

# <Idea Name>

## Idea

> (executive summary — written at distill; leave placeholder during interview)

## Goal

> (success criteria and feature list — written at distill; leave placeholder during interview)

## Interview Results
```

**Properties (YAML frontmatter):** Document metadata for search and
organization. Always include:

| Field | When | Content |
|-------|------|---------|
| `title` | Phase 1 | Idea name (human-readable) |
| `tags` | Phase 1 → refine at distill | Always include `inception` and `<slug>`; add 2–5 domain tags (lowercase, kebab-case or single words) inferred from the idea name and opening brief |
| `keywords` | Phase 1 → refine at distill | 3–8 search terms: products, users, capabilities, systems mentioned |
| `incepted` | Phase 1 | `YYYY-MM-DD` |

At Phase 1, populate `tags` and `keywords` from whatever is known (idea name,
slug, repos/products in the opening brief). Refine both at distill from the
full interview — do not leave `keywords: []` after distill.


## Phase 2 — Codebase Orientation

If working in an existing codebase, orient before planning:

- Scan repo root for structure (package.json, go.mod, pyproject.toml, etc.)
- Note language, framework, established patterns, test framework, linter config
- Identify existing files that will be modified (not just created)
- Note the project's commit style (conventional commits, etc.)

Follow existing patterns. Don't propose new structure unless the design
explicitly calls for it.

If greenfield, note it and proceed.


## Phase 3 — Scope Check

Assess whether this is one plan or several:

- If the design covers multiple independent subsystems, suggest one plan per
  subsystem: "This design spans N independent subsystems. I'd recommend separate
  plans — each produces working, testable software on its own. Start with
  [most logical first piece]?"
- Don't write a 40-task plan when it should be three 12-task plans.


## Phase 4 — File Responsibility Map

Before writing any tasks, map out every file that will be created or modified.
This is where decomposition decisions get locked in.

```markdown
## File Map

| File | Action | Responsibility |
|---|---|---|
| `src/auth/middleware.ts` | Create | Validates JWT tokens, attaches user to request context |
| `src/auth/middleware.test.ts` | Create | Unit tests for auth middleware |
| `src/routes/index.ts` | Modify (L23-30) | Mount auth middleware on protected routes |
```

Rules:
- Each file has **one clear responsibility**
- Files that change together should live together
- Prefer smaller, focused files over large multi-purpose ones
- In existing codebases, follow established patterns — don't restructure
  unilaterally
- Flag any file that's growing unwieldy and include a split in the plan if
  warranted


## Phase 5 — Write Tasks

### Task Sizing

Each task is **one action, 2-5 minutes of work**. These are separate tasks, not
one task:

- Write the failing test → task
- Run it to confirm it fails → task
- Write minimal implementation to pass → task
- Run tests to confirm green → task
- Commit → task

### Task Format

````markdown
### Task N: [Short Description]

**Files:**
- Create: `exact/path/to/file.ts`
- Modify: `exact/path/to/existing.ts` (lines ~45-60)
- Test: `tests/exact/path/to/file.test.ts`

- [ ] **Step 1: [Action]**

```typescript
// Complete code — not pseudocode, not "implement X here"
export function validateToken(token: string): UserContext {
  // actual implementation
}
```

- [ ] **Step 2: Verify**

Run: `npm test -- --testPathPattern=auth.middleware`
Expected: PASS — 3 tests passing

- [ ] **Step 3: Commit**

```bash
git add src/auth/middleware.ts tests/auth/middleware.test.ts
git commit -m "feat: add JWT validation middleware"
```
````

### Task Ordering

- Dependencies flow downward — Task N never depends on Task N+1
- Group by feature slice, not by technical layer (don't do "all models, then
  all routes, then all tests")
- Each task should leave the codebase in a working state after its commit
- If Task N fails, Tasks 1 through N-1 should still be valid

### TDD Flow (when the project has tests)

Follow red-green-refactor:
1. Write the failing test (red)
2. Verify it fails
3. Write minimal code to pass (green)
4. Verify it passes
5. Refactor if needed
6. Commit

For projects without a test framework, include verification steps that use the
appropriate tool (curl, browser check, CLI output, etc.).


## Phase 6 — No Placeholders

Every step must contain what the executor needs. These are **plan failures** —
scan for and fix them:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the content — executor may read tasks out of order)
- Steps that describe what to do without showing how
- References to types, functions, or methods not defined in any task
- Vague verification: "make sure it works" (specify the exact command and
  expected output)


## Phase 7 — Self-Review

Run this checklist silently. Fix issues inline — don't ask the user.

1. **Spec/design coverage** — skim each requirement in the source document. Can
   you point to a task that implements it? List gaps, add missing tasks.
2. **Placeholder scan** — search for every pattern in Phase 6. Fix them all.
3. **Type consistency** — do names, signatures, and interfaces agree across all
   tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in
   Task 7 is a bug.
4. **Dependency ordering** — does any task reference something created in a later
   task? Reorder if so.
5. **Verification completeness** — does every task have a concrete verification
   step with an expected outcome?


## Phase 8 — Plan Document Structure

The complete plan document follows this structure:

```markdown
# [Feature Name] Implementation Plan

*Created: YYYY-MM-DD*

**Goal:** [One sentence]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**Source:** [Link to design.md / spec.md / ticket]


## File Map

| File | Action | Responsibility |
|---|---|---|
| ... | ... | ... |


## Tasks

### Task 1: ...

### Task 2: ...

(etc.)


## Verification Summary

Final verification steps after all tasks complete:
- [ ] All tests pass: `<command>`
- [ ] App starts clean: `<command>`
- [ ] Feature works end-to-end: `<manual verification steps>`
```


## Phase 9 — Save

Save under `$ARTIFACT_DIR/<scope>/<slug>/`:

- **Path:** `$ARTIFACT_DIR/<scope>/<slug>/<slug>-plan.md`
  - Resolve `<scope>` per the artifact-dir rule — from cwd, from a
    `for <customer>` phrase, or empty for the flat fallback case
- **Never** truncate — full plan only
- Use `-v2` suffix if file already exists
- Add `*Created: YYYY-MM-DD*` under the title
- Open in editor/vault if integration is configured

Confirm: `Saved: $ARTIFACT_DIR/<scope>/<slug>/<slug>-plan.md`


## Phase 10 — Execution Handoff

After saving, present execution options:

> "Plan saved. How do you want to execute?"
>
> 1. **Subagent per task** — I dispatch a fresh agent for each task in an
>    isolated worktree. Best for larger plans where context bleed is a risk.
> 2. **Inline execution** — I work through the tasks in this session. Faster for
>    smaller plans.
> 3. **Manual** — You (or another session) pick up the plan and work through it.
>    The plan is self-contained.

Wait for the user's choice before proceeding.


## Key Principles

- **Zero-context executor** — every task is self-contained, complete code, exact
  paths
- **2-5 minute tasks** — if it takes longer, break it down further
- **No placeholders** — scan and fix before saving
- **TDD when possible** — red-green-refactor, verify at every step
- **Feature slices, not layers** — group by what the user sees, not by technical
  layer
- **Working state after every commit** — no task leaves the codebase broken
- **Artifact rules** — `$ARTIFACT_DIR/<scope>/<slug>/` only, never truncate
